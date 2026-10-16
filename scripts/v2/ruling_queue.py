#!/usr/bin/env python3
"""Hyperlex v2 daily human ruling queue.

pick   -> rulings/queue/<date>.jsonl + .md (50 rows, stratified by term,
          unruled terms first, test-split need first)
apply  -> appends human rulings to rulings/landing/human_rulings.v1.jsonl
          (IDs + ruling only, no post text); optional --write-sqlite adds
          operator_definitions rows (never overwrites, backup first);
          never writes term-level status (spec 009 Q1: R is an
          excerpt-level extraction fact; auto-reject removed 2026-10-16).
          R rulings get row_status TARGET_ABSENT -> extraction repair.
          --answers accepts several files (multi-part replies), inline
          comma-separated entries ("PART 1: 004 O, 013 S"), and a
          corrections-only mode (unlisted rows keep the model label).
          --update-existing revises already-landed rulings in place.
status -> landing totals vs the gold-eval need
Source DB is opened read-only except under apply --write-sqlite.
"""
import argparse, datetime, glob, hashlib, json, os, re, shutil, sqlite3, sys
from collections import Counter, defaultdict

RULE_VERSION = "hyperlex.ruling.v1"
SPLIT_METHOD_VERSION = "slang.split.v1"
DEFAULT_DB = "/workspace/vernacular-ingest/data/vernacular.sqlite3"
DEFAULT_ROOT = "/workspace/hyperlex-v2-tracker/rulings"
ALLOWED_SENSE = {"SLANG_SENSE", "OTHER_SENSE", "UNSURE", "REJECT"}
GOLD = {"SLANG_SENSE", "OTHER_SENSE"}
CODES = {"S": "SLANG_SENSE", "O": "OTHER_SENSE", "U": "UNSURE", "R": "REJECT"}
TEST_TARGET = 470
TEST_USES_PER_TERM = 10  # Danny 2026-10-11: ruled test terms may return until this many gold uses
TEST_PER_QUEUE = 3  # Danny 2026-10-15 18:00 PT: test terms up to 3 rows/term per queue, only if never in train/val
TRAINVAL_USES_PER_TERM = 10  # Danny 2026-10-11 15:31 PT: same return rule for train/val
HANDLE = re.compile(r"(?<![\w@])@[A-Za-z0-9_]{1,15}")

CORRECTIONS_MARKER = "corrections only"
RETAINED_NOTE = "corrections-only: model proposal retained"
INDEX_START = re.compile(r"\d{1,3}(?!\d)")
SECTION_LABEL = re.compile(r"^(?:part\s*\d+|test|val|validation|train|training)\s*[:\-]\s*", re.I)
ENTRY = re.compile(r"(\d{1,3})\s*[:.)\-]?\s*([A-Za-z]+)[.;:]?(?:\s+(.*))?", re.S)
ENTRY_SPLIT = re.compile(r"\s*,\s*(?=\d{1,3}\s*[:.)\-]?\s*[A-Za-z]+\b)")


def split_for(family):
    b = int(hashlib.sha256(f"{SPLIT_METHOD_VERSION}:{family}".encode()).hexdigest(), 16) % 100
    return "train" if b < 80 else "val" if b < 90 else "test"


def jl(v):
    try:
        return json.loads(v) if v else {}
    except Exception:
        return {}


def paths(root):
    p = {k: os.path.join(root, k) for k in ("queue", "answered", "landing", "backups")}
    for d in p.values():
        os.makedirs(d, exist_ok=True)
    p["landing_file"] = os.path.join(p["landing"], "human_rulings.v1.jsonl")
    return p


def queue_stem(date, suffix=""):
    """Filename stem for a queue: YYYY-MM-DD or YYYY-MM-DDsuffix (e.g. 2026-10-11b)."""
    s = suffix or ""
    if s and not re.fullmatch(r"[A-Za-z0-9_-]+", s):
        raise SystemExit(f"invalid --suffix {suffix!r}: use letters, digits, _ or -")
    return date + s


def load_landing(p):
    if not os.path.exists(p["landing_file"]):
        return []
    return [json.loads(l) for l in open(p["landing_file"]) if l.strip()]


def ro(db):
    return sqlite3.connect(f"file:{db}?mode=ro", uri=True)


def table_ids(con, table):
    try:
        return {r[0] for r in con.execute(f"SELECT term_id FROM {table}")}
    except sqlite3.Error:
        return set()


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def pending_ids(p, today):
    ids = set()
    cutoff = (datetime.date.fromisoformat(today[:10]) - datetime.timedelta(days=14)).isoformat()
    for f in glob.glob(os.path.join(p["queue"], "*.jsonl")):
        stem = os.path.splitext(os.path.basename(f))[0]
        d = stem[:10]
        if d < cutoff or glob.glob(os.path.join(p["answered"], stem + ".*")):
            continue
        ids |= {json.loads(l)["observation_id"] for l in open(f) if l.strip()}
    return ids


def terms_in_date_queues(p, date):
    """term_ids already present in any queue for this calendar date (any suffix)."""
    terms = set()
    for f in glob.glob(os.path.join(p["queue"], f"{date}*.jsonl")):
        stem = os.path.splitext(os.path.basename(f))[0]
        if not stem.startswith(date):
            continue
        terms |= {json.loads(l)["term_id"] for l in open(f) if l.strip()}
    return terms


def cmd_pick(a):
    p = paths(a.root)
    stem = queue_stem(a.date, getattr(a, "suffix", "") or "")
    qf = os.path.join(p["queue"], stem + ".jsonl")
    if os.path.exists(qf) and not a.force:
        sys.exit(f"queue exists: {qf} (use --force)")
    landing = load_landing(p)
    done = {r["observation_id"] for r in landing}
    skip = done | (set() if a.force else pending_ids(p, a.date))
    con = ro(a.db)
    ruled = table_ids(con, "operator_definitions") | table_ids(con, "operator_term_status")
    per_term = Counter(r["term_id"] for r in landing if r.get("sense") in GOLD)
    ruled |= set(per_term)
    tids_in_date = terms_in_date_queues(p, a.date)
    skip_terms = set(ruled) | tids_in_date
    test_have = sum(1 for r in landing if r.get("split") == "test" and r.get("sense") in GOLD)
    trainval_terms = {r["term_id"] for r in landing if r.get("split") in ("train", "val")}
    rows = con.execute(
        "SELECT os.observation_id, os.term_id, os.label, os.prob, t.canonical_form, t.payload, o.payload "
        "FROM observation_sense_v1 os JOIN observations o ON o.observation_id=os.observation_id "
        "JOIN terms t ON t.term_id=os.term_id").fetchall()
    by_term = defaultdict(list)
    meta = {}
    for oid, tid, label, prob, canon, tp, op in rows:
        if oid in skip:
            continue
        fam = str(jl(tp).get("hyperlex_lineage_family") or canon).lower()
        split = split_for(fam)
        if split == "test":
            reopen = (test_have < TEST_TARGET
                      and per_term[tid] < TEST_USES_PER_TERM
                      and tid not in trainval_terms)
        else:
            reopen = (per_term[tid] < TRAINVAL_USES_PER_TERM
                      and tid not in tids_in_date)
        if tid in skip_terms and not reopen:
            continue
        obs = jl(op)
        text = obs.get("raw_excerpt") or obs.get("text")
        if not text:
            continue
        fam = str(jl(tp).get("hyperlex_lineage_family") or canon).lower()
        by_term[tid].append({"observation_id": oid, "term_id": tid, "term": canon, "term_family": fam,
                             "split": split_for(fam), "model_label": label, "model_prob": prob,
                             "text": HANDLE.sub("@user", text)})
        meta[tid] = (canon, fam, split_for(fam))

    def tkey(tid):
        canon, fam, split = meta[tid]
        need = 0 if (split == "test" and test_have < TEST_TARGET) else (1 if split == "val" else 2)
        return (0 if tid not in ruled else 1, need, per_term[tid], canon)

    for tid, lst in by_term.items():
        c = Counter(r["model_label"] for r in lst)
        unc = lambda r: (abs((r["model_prob"] if r["model_prob"] is not None else 0.5) - 0.5), r["observation_id"])
        groups = {lab: sorted([r for r in lst if r["model_label"] == lab], key=unc) for lab in c}
        order = sorted(groups, key=lambda lab: c[lab])  # rarer label first
        out = []
        while any(groups.values()):
            for lab in order:
                if groups[lab]:
                    out.append(groups[lab].pop(0))
        by_term[tid] = out
    terms = sorted(by_term, key=tkey)
    picked, taken = [], Counter()
    while len(picked) < a.n:
        progress = False
        for tid in terms:
            if len(picked) >= a.n:
                break
            if meta[tid][2] == "test":
                cap = min(TEST_PER_QUEUE, TEST_USES_PER_TERM - per_term[tid])
            else:
                cap = min(a.per_term, TRAINVAL_USES_PER_TERM - per_term[tid])
            if taken[tid] < cap and taken[tid] < len(by_term[tid]):
                picked.append(by_term[tid][taken[tid]])
                taken[tid] += 1
                progress = True
        if not progress:
            break
    lines, md = [], [f"# Hyperlex ruling queue {stem}", "",
                     "Answer per row: S = slang sense, O = other sense, U = unsure, R = reject. "
                     "Optional definition after the code, e.g. `004 S praise that goes way over the top`.", ""]
    for i, r in enumerate(picked, 1):
        reasons = ["unruled_term" if r["term_id"] not in ruled else "ruled_term"]
        if r["split"] == "test" and test_have < TEST_TARGET:
            reasons.append("test_need")
        rec = {"queue_id": f"{stem}:{i:03d}", "rule_version": RULE_VERSION, "queue_date": a.date, **r,
               "priority_reason": ",".join(reasons), "answer": {"sense": None, "definition": None, "notes": None}}
        lines.append(json.dumps(rec, ensure_ascii=False))
        prob = "n/a" if r["model_prob"] is None else f"{r['model_prob']:.2f}"
        md += [f"### {i:03d} {r['term']} ({r['split']})", "", "> " + r["text"].replace("\n", "\n> "), "",
               f"model: {r['model_label']} ({prob})", "", "answer: ", ""]
    with open(qf, "w") as f:
        f.write("\n".join(lines) + ("\n" if lines else ""))
    with open(qf[:-6] + ".md", "w") as f:
        f.write("\n".join(md))
    print(json.dumps({"queue_jsonl": qf, "queue_md": qf[:-6] + ".md", "rows": len(picked),
                      "distinct_terms": len(taken), "unruled_terms": sum(1 for t in taken if t not in ruled),
                      "test_rows": sum(1 for r in picked if r["split"] == "test"),
                      "test_gold_have": test_have, "test_target": TEST_TARGET}, indent=2))


def _as_list(x):
    if x is None:
        return []
    return [x] if isinstance(x, str) else list(x)


def _iter_sources(lines_or_files):
    """Yield (source_label, line). Items that are existing file paths are read; others are lines."""
    for i, item in enumerate(_as_list(lines_or_files)):
        if isinstance(item, str) and "\n" not in item and os.path.isfile(item):
            with open(item) as f:
                for line in f.read().splitlines():
                    yield os.path.basename(item), line
        elif isinstance(item, str):
            for line in item.splitlines() or [""]:
                yield "<inline>", line


def parse_answers(lines_or_files, valid=None, ignored=None):
    """Parse answer lines/files in order.

    Returns (dict idx(3-digit str) -> (code letter, definition or None), corrections_only_bool).
    Prose / section-header lines are skipped silently. Lines starting with a 1-3 digit index
    that are malformed or out of range (when `valid` is given) are reported: appended to
    `ignored` if it is a list, otherwise printed as "ignored line: ...".
    Same index with different codes -> sys.exit; same code twice is fine.
    """
    out, origin = {}, {}
    corrections_only = False

    def report(s):
        if isinstance(ignored, list):
            ignored.append(s)
        else:
            print(f"ignored line: {s}")

    for src, raw in _iter_sources(lines_or_files):
        line = raw.strip()
        if not line:
            continue
        if line.lower().startswith(CORRECTIONS_MARKER):
            corrections_only = True
            line = line[len(CORRECTIONS_MARKER):].lstrip(" \t:-—").strip()
            if not line:
                continue
        if line.startswith("#"):
            continue
        line = SECTION_LABEL.sub("", line, count=1).strip()
        if not INDEX_START.match(line):
            continue  # prose / section header: skip silently
        for seg in ENTRY_SPLIT.split(line):
            seg = seg.strip().rstrip(",").strip()
            if not seg:
                continue
            m = ENTRY.fullmatch(seg)
            if not m or m.group(2).upper() not in CODES:
                report(seg)
                continue
            idx = m.group(1).zfill(3)
            if valid is not None and idx not in valid:
                report(seg)
                continue
            code = m.group(2).upper()
            definition = (m.group(3) or "").strip() or None
            if idx in out:
                old_code, old_def = out[idx]
                if old_code != code:
                    sys.exit(f"conflicting answers for {idx}: {old_code} ({origin[idx]}) vs {code} ({src})")
                if definition and not old_def:
                    out[idx] = (code, definition)
                continue
            out[idx] = (code, definition)
            origin[idx] = src
    return out, corrections_only


TARGET_ABSENT = "TARGET_ABSENT"
NON_GOLD_ROW_STATUS = {TARGET_ABSENT}


def target_absent_fields(at):
    """Spec 009 Q5: R = target absent from the excerpt -> row-level status, extraction repair.
    Kept out of gold, cohorts and attestation; the R label stays as history."""
    return {"row_status": TARGET_ABSENT, "repair_route": "extraction_repair", "row_status_at": at}


def ratification_ref(srcs):
    """First 'corrections only' line of the answers files, as the human ratification (DEC-010)."""
    for f in srcs:
        try:
            for line in open(f):
                if line.strip().lower().startswith("corrections only"):
                    return {"file": os.path.basename(f), "text": line.strip()}
        except OSError:
            pass
    return None


def is_gold(r):
    return r.get("sense") in GOLD and r.get("row_status") not in NON_GOLD_ROW_STATUS


def expand_corrections(queue_rows, corrections):
    """Corrections-only expansion: listed rows get the given code, all others keep model_label."""
    out = []
    for r in queue_rows:
        r = dict(r)
        idx = r["queue_id"][-3:]
        if idx in corrections:
            code, definition = corrections[idx]
            r["answer"] = {"sense": CODES.get(str(code).upper(), code), "definition": definition, "notes": None}
            r["answer_mode"] = "corrections_only_listed"
        else:
            lab = r.get("model_label")
            if lab not in ALLOWED_SENSE:
                sys.exit(f"corrections-only: model_label {lab!r} of {r['queue_id']} not in allowed senses")
            r["answer"] = {"sense": lab, "definition": None, "notes": RETAINED_NOTE}
            r["answer_mode"] = "corrections_only_retained"
        out.append(r)
    return out


def read_answers(a, p):
    if getattr(a, "file", None):
        recs = [json.loads(l) for l in open(a.file) if l.strip()]
        for r in recs:
            r.setdefault("answer_mode", "explicit")
        return recs, [a.file]
    files = _as_list(a.answers)
    for f in files:
        if not os.path.isfile(f):
            sys.exit(f"answers file not found: {f}")
    qf = os.path.join(p["queue"], a.date + ".jsonl")
    queue = {json.loads(l)["queue_id"][-3:]: json.loads(l) for l in open(qf) if l.strip()}
    ignored = []
    corrections, auto = parse_answers(files, valid=set(queue), ignored=ignored)
    for s in ignored:
        print(f"ignored line: {s}")
    co = bool(getattr(a, "corrections_only", False)) or (auto and not getattr(a, "no_auto_corrections", False))
    rows = list(queue.values())
    if co:
        recs = expand_corrections(rows, corrections)
    else:
        recs = []
        for r in rows:
            r = dict(r)
            idx = r["queue_id"][-3:]
            if idx in corrections:
                code, definition = corrections[idx]
                r["answer"] = {"sense": CODES[code], "definition": definition, "notes": None}
                r["answer_mode"] = "explicit"
            recs.append(r)
    return recs, files


def _write_answered(p, date, srcs):
    if len(srcs) == 1:
        src = srcs[0]
        shutil.copy(src, os.path.join(p["answered"], date + os.path.splitext(src)[1]))
        return
    with open(os.path.join(p["answered"], date + ".answers.txt"), "w") as out:
        for src in srcs:
            out.write(f"# --- {os.path.basename(src)}\n")
            with open(src) as f:
                txt = f.read()
            out.write(txt if txt.endswith("\n") or not txt else txt + "\n")


def cmd_apply(a):
    p = paths(a.root)
    recs, srcs = read_answers(a, p)
    revision_source = ", ".join(os.path.basename(s) for s in srcs)
    ratification = ratification_ref(srcs)
    landing = load_landing(p)
    pos = {(r["observation_id"], r["term_id"]): i for i, r in enumerate(landing)}
    update_existing = getattr(a, "update_existing", False)
    new, unanswered, updated = [], [], []
    unchanged = 0
    for r in recs:
        ans = r.get("answer") or {}
        sense = ans.get("sense")
        if not sense:
            unanswered.append(r["queue_id"])
            continue
        if sense not in ALLOWED_SENSE:
            sys.exit(f"bad sense {sense!r} in {r['queue_id']}")
        mode = r.get("answer_mode", "explicit")
        key = (r["observation_id"], r["term_id"])
        if key in pos:
            i = pos[key]
            if i is None:  # already added as new in this batch
                unchanged += 1
                continue
            old = landing[i]
            if (update_existing and mode != "corrections_only_retained"
                    and old.get("sense") != sense):
                upd = dict(old)
                upd["revised_from"] = old.get("sense")
                upd["revised_at"] = now_iso()
                upd["revision_source"] = revision_source
                upd["sense"] = sense
                if ans.get("definition"):
                    upd["definition"] = ans["definition"]
                upd["answer_mode"] = mode
                if sense == "REJECT":
                    upd.update(target_absent_fields(upd["revised_at"]))
                landing[i] = upd
                updated.append(upd)
            else:
                unchanged += 1
            continue
        at = now_iso()
        new.append({"ruling_id": hashlib.sha256(f"{RULE_VERSION}:{r['observation_id']}:{r['term_id']}:{at}".encode()).hexdigest(),
                    "rule_version": RULE_VERSION, "observation_id": r["observation_id"], "term_id": r["term_id"],
                    "term": r["term"], "term_family": r["term_family"], "split": r["split"], "sense": sense,
                    "definition": ans.get("definition"), "notes": ans.get("notes"), "by": a.by, "at": at,
                    "source": "human", "queue_id": r["queue_id"], "model_label": r.get("model_label"),
                    "model_prob": r.get("model_prob"), "answer_mode": mode})
        if mode == "corrections_only_retained" and ratification:
            new[-1]["ratification_ref"] = ratification
        if sense == "REJECT":
            new[-1].update(target_absent_fields(at))
        pos[key] = None
    modes = Counter(r.get("answer_mode") for r in recs if (r.get("answer") or {}).get("sense"))
    print(json.dumps({"new_rulings": len(new), "updated": len(updated), "unchanged": unchanged,
                      "unanswered": len(unanswered),
                      "listed": modes["corrections_only_listed"] + modes["explicit"],
                      "retained": modes["corrections_only_retained"],
                      "by_sense": Counter(n["sense"] for n in new)}, indent=2))
    if a.dry_run:
        for n in new:
            print(json.dumps(n))
        for u in updated:
            print(json.dumps({"update": u}))
        return
    if updated:
        tmp = p["landing_file"] + ".tmp"
        with open(tmp, "w") as f:
            for r in landing + new:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        os.replace(tmp, p["landing_file"])
    else:
        with open(p["landing_file"], "a") as f:
            for n in new:
                f.write(json.dumps(n, ensure_ascii=False) + "\n")
    _write_answered(p, a.date, srcs)
    if a.write_sqlite and (new or updated):
        stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
        bk = os.path.join(p["backups"], f"vernacular.{stamp}.sqlite3")
        s, d = sqlite3.connect(a.db), sqlite3.connect(bk)
        s.backup(d)
        d.close()
        defs = stat = 0
        existing = table_ids(s, "operator_definitions")
        by_term = defaultdict(list)
        for n in new:
            by_term[n["term_id"]].append(n)
        for tid, lst in by_term.items():
            dn = next((n for n in lst if n["definition"]), None)
            if dn and tid not in existing:
                s.execute("INSERT INTO operator_definitions(term_id, definition, defined_by, defined_at, source) "
                          "VALUES (?,?,?,?,?)", (tid, dn["definition"], a.by, dn["at"],
                                                 f"{RULE_VERSION} ruling queue {dn['queue_id']}"))
                defs += 1
        s.commit()
        s.close()
        print(json.dumps({"sqlite_backup": bk, "operator_definitions_added": defs,
                          "operator_term_status_added": stat}, indent=2))


def cmd_status(a):
    p = paths(a.root)
    L = load_landing(p)
    gold = [r for r in L if is_gold(r)]
    pend = []
    for f in sorted(glob.glob(os.path.join(p["queue"], "*.jsonl"))):
        stem = os.path.splitext(os.path.basename(f))[0]
        if not glob.glob(os.path.join(p["answered"], stem + ".*")):
            pend.append(os.path.basename(f))
    print(json.dumps({"rulings": len(L), "gold_rulings": len(gold), "distinct_terms": len({r["term_id"] for r in L}),
                      "gold_terms": len({r["term_id"] for r in gold}), "by_sense": Counter(r["sense"] for r in L),
                      "by_split_gold": Counter(r["split"] for r in gold),
                      "test_gold": sum(1 for r in gold if r["split"] == "test"), "test_target": TEST_TARGET,
                      "pending_queues": pend}, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--db", default=DEFAULT_DB)
    sub = ap.add_subparsers(dest="cmd", required=True)
    today = datetime.date.today().isoformat()
    pk = sub.add_parser("pick")
    pk.add_argument("--n", type=int, default=300)
    pk.add_argument("--per-term", type=int, default=10)
    pk.add_argument("--date", default=today)
    pk.add_argument("--suffix", default="", help="extra queue same day, e.g. b -> YYYY-MM-DDb.jsonl")
    pk.add_argument("--force", action="store_true")
    ar = sub.add_parser("apply")
    g = ar.add_mutually_exclusive_group(required=True)
    g.add_argument("--file", help="answered queue jsonl (answer.sense filled)")
    g.add_argument("--answers", nargs="+",
                   help="text file(s): '001 S', '002 O def...', U, R; 'PART 1: 004 O, 013 S' ok")
    ar.add_argument("--date", default=today)
    ar.add_argument("--by", default="Danny")
    ar.add_argument("--write-sqlite", action="store_true")
    ar.add_argument("--dry-run", action="store_true")
    ar.add_argument("--corrections-only", action="store_true",
                    help="unlisted rows keep their model_label")
    ar.add_argument("--no-auto-corrections", action="store_true",
                    help="disable 'corrections only' autodetection in answers files")
    ar.add_argument("--update-existing", action="store_true",
                    help="revise already-landed rulings whose sense differs")
    sub.add_parser("status")
    a = ap.parse_args()
    {"pick": cmd_pick, "apply": cmd_apply, "status": cmd_status}[a.cmd](a)


if __name__ == "__main__":
    main()
