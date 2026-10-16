#!/usr/bin/env python3
# Mirror of the operator-box Jev sense labeller (spec 009 T028, 2026-10-16); paths generalized.
# PROVENANCE: NEW 2026-09-25 PT (Danny 10:50 PT). Additive: writes only table observation_sense_v1.
"""Per-observation sense labels (SLANG_SENSE | OTHER_SENSE | UNKNOWN) via Jev, batched per term.

Only observations of tracked terms (observations.term_canonical = terms.canonical_form) that have no
label under the current sense contract version are sent (incremental: the daily export only labels
new observations).

Usage: sense_labels.py [--backfill] [--dry-run] [--max-cost-usd 1.0]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = Path(os.environ.get("VERN_DB", "data/vernacular.sqlite3"))
SENSE_CONTRACT = Path(os.environ.get("SENSE_CONTRACT", HERE / "jev_sense_contract.json"))  # spec 009 T028: point at a rebuilt-sense-v2 contract to emit use_mention
JEV_CLIENT = Path(os.environ.get("JEV_CLIENT", str(HERE / "jev_client.mjs")))
CACHE = HERE / "receipts" / "jev-cache"
PRICE = 0.042  # USD per 1M input tokens (TypeSafe jev-1.13), output free
LABELS = ("SLANG_SENSE", "OTHER_SENSE", "UNKNOWN")
UM_SUFFIX = "_um"  # spec 009 T028: per-post use/mention question id suffix


def contract() -> dict:
    return json.loads(SENSE_CONTRACT.read_text())


def contract_sha() -> str:
    return hashlib.sha256(SENSE_CONTRACT.read_bytes()).hexdigest()


def ensure_table(con) -> None:
    con.execute("""CREATE TABLE IF NOT EXISTS observation_sense_v1 (
        observation_id TEXT PRIMARY KEY, term_id TEXT NOT NULL, label TEXT NOT NULL, prob REAL,
        contract_version TEXT NOT NULL, computed_at TEXT NOT NULL)""")
    cols = {r[1] for r in con.execute("PRAGMA table_info(observation_sense_v1)")}
    if "use_mention" not in cols:  # additive (spec 009 T028); NULL = not labelled (read as USE under v1.4)
        con.execute("ALTER TABLE observation_sense_v1 ADD COLUMN use_mention TEXT")


def load_labels(db: Path = DB, version: str | None = None) -> dict:
    """{observation_id: (label, prob)} for the current sense contract version ({} if table absent)."""
    version = version or contract()["version"]
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=120)
    try:
        rows = con.execute("SELECT observation_id, label, prob FROM observation_sense_v1 WHERE contract_version=?",
                           (version,)).fetchall()
    except sqlite3.OperationalError as e:
        if "no such table" not in str(e):
            raise  # 11:33 PT fix: a lock (discovery lane writing) must fail loudly, never read as "no rows"
        rows = []
    con.close()
    return {r[0]: (r[1], r[2]) for r in rows}


def pending(db: Path = DB) -> dict:
    """{term_id: {"cf", "p", "obs": [(observation_id, text)]}} of unlabeled tracked-term observations."""
    have = load_labels(db)
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=120)
    terms = {cf: (tid, json.loads(pl)) for tid, cf, pl in con.execute("SELECT term_id, canonical_form, payload FROM terms")}
    out = {}
    for oid, cf, pl, created in con.execute(
            "SELECT observation_id, term_canonical, payload, created_at FROM observations ORDER BY created_at, observation_id"):
        if cf not in terms or oid in have:
            continue
        tid, p = terms[cf]
        o = json.loads(pl)
        out.setdefault(tid, {"cf": cf, "p": p, "obs": []})["obs"].append((oid, o.get("text") or o.get("raw_excerpt") or ""))
    con.close()
    return out


def build_request(cf: str, p: dict, batch: list, c: dict) -> dict:
    posts = [{"id": f"p{i}", "text": (txt or "")[: c["max_post_chars"]]} for i, (_, txt) in enumerate(batch)]
    qt = c["question_template"]
    qs = {x["id"]: {"type": qt["type"], "instructions": qt["instructions"].format(pid=x["id"], term=cf),
                    "criteria": qt["criteria"]} for x in posts}
    if c.get("closed_set_use_mention"):  # rebuilt-sense-v2: one extra USE/MENTION choice per post
        for x in posts:
            qs[x["id"] + UM_SUFFIX] = {"type": "choice",
                                      "instructions": f"Post {x['id']} in STATE.posts: does it USE the term '{cf}' to convey meaning, "
                                                      "or MENTION it (define, quote, ask what it means, comment on its form)? "
                                                      f"A definition embedded inside a genuine use is USE. Judge only post {x['id']}.",
                                      "criteria": qt.get("criteria_use_mention") or {k: k for k in c["closed_set_use_mention"]}}
    state = {"term": cf, "recorded_slang_meaning": p.get("current_summary") or "",
             "possible_meanings": p.get("possible_meanings") or [], "posts": posts}
    return {"state": state, "questions": qs, "model": c.get("model", "jev-latest")}


def estimate(req: dict) -> float:
    return len(json.dumps(req)) / 4 * 2 * 2 * PRICE / 1e6


def _tok(v) -> int:
    if isinstance(v, dict):
        v = v.get("total", v.get("noCache", 0))
    try:
        return int(v or 0)
    except (TypeError, ValueError):
        return 0


def call(req: dict, csha: str, dry_run: bool) -> tuple[dict, bool]:
    h = hashlib.sha256(json.dumps(req, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    cp = CACHE / f"sense_{csha[:12]}_{h}.json"
    if cp.exists():
        try:
            return json.loads(cp.read_text()), True
        except Exception:
            pass
    try:
        pr = subprocess.run(["node", str(JEV_CLIENT)], input=json.dumps(req), capture_output=True, text=True, timeout=180)
        res = json.loads((pr.stdout.strip().splitlines() or ["{}"])[-1])
    except Exception as e:
        return {"ok": False, "error_class": "jev_call_error", "error": type(e).__name__}, False
    if res.get("ok") and (res.get("backend") != "typesafe" or res.get("dry_run") or res.get("emulated")):
        return {"ok": False, "error_class": "not_real_jev", "error": f"backend={res.get('backend')}"}, False
    if res.get("ok") and not dry_run:
        CACHE.mkdir(parents=True, exist_ok=True)
        cp.write_text(json.dumps(res))
    return res, False


def parse_answer(answers: dict, pid: str, c: dict) -> tuple:
    """(label, prob, use_mention) for one post. Fail closed: missing/out-of-set/low-prob sense -> UNKNOWN;
    missing/out-of-set use_mention -> None (unlabelled). Contract v2 rule: a MENTION is never SLANG_SENSE."""
    min_p = float(c["min_top_probability"])
    a = answers.get(pid)
    lab, prob = "UNKNOWN", None
    if isinstance(a, dict) and a.get("choice") in c["closed_set"]:
        try:
            prob = float((a.get("probabilities") or {}).get(a["choice"]))
        except (TypeError, ValueError):
            prob = None
        lab = a["choice"] if prob is not None and prob >= min_p else "UNKNOWN"
    um = None
    if c.get("closed_set_use_mention"):
        b = answers.get(pid + UM_SUFFIX)
        if isinstance(b, dict) and b.get("choice") in c["closed_set_use_mention"]:
            try:
                up = float((b.get("probabilities") or {}).get(b["choice"]))
            except (TypeError, ValueError):
                up = None
            um = b["choice"] if up is not None and up >= min_p else None
        if um == "MENTION" and lab == "SLANG_SENSE":
            lab = "OTHER_SENSE"
    return lab, prob, um


def label_pending(db: Path = DB, max_cost_usd: float = 1.0, dry_run: bool = False, allow_live: bool = True,
                  only: set | None = None) -> dict:
    """Label every pending observation (only the given canonical forms if `only`; export --only scoping, 2026-09-25 11:13 PT).
    Returns stats incl. terms whose labeling is incomplete (fail closed)."""
    c = contract(); csha = contract_sha(); ver = c["version"]; min_p = float(c["min_top_probability"])
    todo = pending(db)
    if only:
        todo = {k: v for k, v in todo.items() if v["cf"] in only}
    stats = {"sense_contract_version": ver, "sense_contract_sha256": csha, "pending_posts": sum(len(v["obs"]) for v in todo.values()),
             "pending_terms": len(todo), "batches": 0, "live_calls": 0, "cache_hits": 0, "labeled": 0,
             "labels": {k: 0 for k in LABELS}, "incomplete_terms": [], "errors": [], "usage_input_tokens": 0,
             "cost_usd_estimated_pre_call": 0.0}
    if not todo:
        return stats
    con = None if dry_run else sqlite3.connect(db, timeout=30)
    if con:
        with con:
            ensure_table(con)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for tid, v in todo.items():
        obs = v["obs"]
        for i in range(0, len(obs), c["batch_size"]):
            batch = obs[i:i + c["batch_size"]]
            req = build_request(v["cf"], v["p"], batch, c)
            est = estimate(req)
            if not allow_live:
                h = hashlib.sha256(json.dumps(req, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
                if not (CACHE / f"sense_{csha[:12]}_{h}.json").exists():
                    stats["errors"].append({"term": v["cf"], "error_class": "live_disabled"}); stats["incomplete_terms"].append(v["cf"]); break
            elif stats["cost_usd_estimated_pre_call"] + est > max_cost_usd:
                stats["errors"].append({"term": v["cf"], "error_class": "spend_cap"}); stats["incomplete_terms"].append(v["cf"]); break
            res, hit = call(req, csha, dry_run)
            stats["batches"] += 1
            if hit:
                stats["cache_hits"] += 1
            else:
                stats["live_calls"] += 1; stats["cost_usd_estimated_pre_call"] += est
                stats["usage_input_tokens"] += _tok((res.get("usage") or {}).get("inputTokens"))
            if not res.get("ok"):
                stats["errors"].append({"term": v["cf"], "error_class": res.get("error_class"), "error": str(res.get("error", ""))[:120]})
                stats["incomplete_terms"].append(v["cf"]); break
            rows = []
            for j, (oid, _) in enumerate(batch):
                lab, prob, um = parse_answer(res.get("answers") or {}, f"p{j}", c)
                rows.append((oid, tid, lab, prob, ver, now, um))
                stats["labels"][lab] += 1
                if um:
                    stats.setdefault("use_mention", {}).setdefault(um, 0)
                    stats["use_mention"][um] += 1
            stats["labeled"] += len(rows)
            if con:
                with con:
                    con.executemany("INSERT INTO observation_sense_v1(observation_id, term_id, label, prob, contract_version, computed_at, use_mention) "
                                    "VALUES (?,?,?,?,?,?,?) ON CONFLICT(observation_id) DO UPDATE SET term_id=excluded.term_id, "
                                    "label=excluded.label, prob=excluded.prob, contract_version=excluded.contract_version, "
                                    "computed_at=excluded.computed_at, use_mention=excluded.use_mention", rows)
    if con:
        con.close()
    stats["cost_usd_actual_est"] = round(stats["usage_input_tokens"] * PRICE / 1e6, 6)
    stats["cost_usd_estimated_pre_call"] = round(stats["cost_usd_estimated_pre_call"], 6)
    stats["incomplete_terms"] = sorted(set(stats["incomplete_terms"]))
    return stats


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--backfill", action="store_true", help="one-time backfill of all unlabeled tracked-term observations")
    ap.add_argument("--dry-run", action="store_true", help="count pending only; no Jev calls, no writes")
    ap.add_argument("--max-cost-usd", type=float, default=1.0)
    a = ap.parse_args()
    if a.dry_run:
        pd = pending()
        reqs = [build_request(v["cf"], v["p"], v["obs"][i:i + contract()["batch_size"]], contract())
                for v in pd.values() for i in range(0, len(v["obs"]), contract()["batch_size"])]
        print(json.dumps({"pending_posts": sum(len(v["obs"]) for v in pd.values()), "pending_terms": len(pd),
                          "batches": len(reqs), "cost_usd_estimated_pre_call": round(sum(map(estimate, reqs)), 6)}))
    else:
        cap = a.max_cost_usd if a.backfill else min(a.max_cost_usd, 1.0)
        s = label_pending(max_cost_usd=cap)
        s.setdefault("usage_input_tokens", 0)
        s.setdefault("cost_usd_actual_est", 0.0)
        run = datetime.now().strftime("%Y%m%d-%H%M%S")
        (HERE / "receipts").mkdir(exist_ok=True)
        (HERE / "receipts" / f"sense-{'backfill' if a.backfill else 'run'}-{run}.json").write_text(json.dumps(s, indent=2))
        with (HERE / "ledger.jsonl").open("a") as f:
            f.write(json.dumps({"run_id": f"sense-{run}", "kind": "sense_backfill" if a.backfill else "sense_run",
                                "max_cost_usd": cap, **{k: s.get(k) for k in ("pending_posts", "batches", "live_calls", "labeled",
                                "labels", "incomplete_terms", "usage_input_tokens", "cost_usd_estimated_pre_call", "cost_usd_actual_est",
                                "sense_contract_sha256")}}) + "\n")
        print(json.dumps(s, indent=1))
