#!/usr/bin/env python3
"""G4 BASE audit (draft). Reads private curated JSONL, queries an OpenAI-compatible endpoint
(vLLM on DGX Spark by default), writes private audit JSONL. Never prints post text.

  python scripts/v2/base_audit.py --in /path/private/curated_sense_observation.jsonl \
      --out /path/private/audit_v1.jsonl --endpoint http://spark:8000/v1 --dry-run

--dry-run (default) only counts rows and estimates tokens; --run is required to call the model.
Only rows with a human-settled SLANG/OTHER ruling are audited (fail closed). T2 judge pass: not implemented yet.
"""
import argparse, hashlib, json, os, sys, urllib.request

PROMPT = ("Term: {term}\nContext: {ctx}\n"
          "Is the term used in its slang sense here? Answer SLANG_SENSE or OTHER_SENSE only.")
PROMPT_SHA = hashlib.sha256(PROMPT.encode()).hexdigest()[:12]


def gold_label(r):
    """Human-settled gold only. Candidate/model labels never count as gold (fail closed)."""
    h = r.get("human_ruling") or {}
    if str(h.get("source", "")).lower() != "human":
        return None
    return h.get("sense") if h.get("sense") in ("SLANG_SENSE", "OTHER_SENSE") else None


def select_keep(audited, keep_correct_share, seed="g4-v1"):
    """Keep every row BASE got wrong (target beats BASE); keep a deterministic share of BASE-correct rows."""
    out = []
    wrong = [r for r in audited if not r["base_correct"]]
    right = sorted((r for r in audited if r["base_correct"]),
                   key=lambda r: hashlib.sha256((seed + r["record_id"]).encode()).hexdigest())
    n_right = int(round(keep_correct_share * len(wrong) / max(1e-9, 1 - keep_correct_share))) if keep_correct_share < 1 else len(right)
    keep_right = {r["record_id"] for r in right[:n_right]}
    for r in audited:
        if not r["base_correct"]:
            out.append(dict(r, keep=True, reason="target_beats_base"))
        elif r["record_id"] in keep_right:
            out.append(dict(r, keep=True, reason="base_correct_capped_share"))
        else:
            out.append(dict(r, keep=False, reason="base_already_correct"))
    return out


def ask(endpoint, model, prompt, key=None):
    body = json.dumps({"model": model, "messages": [{"role": "system", "content": "detailed thinking off"},
                       {"role": "user", "content": prompt}], "max_tokens": 8, "temperature": 0}).encode()
    req = urllib.request.Request(endpoint.rstrip("/") + "/chat/completions", body, {"Content-Type": "application/json"})
    if key:
        req.add_header("Authorization", "Bearer " + key)
    out = json.load(urllib.request.urlopen(req, timeout=120))["choices"][0]["message"]["content"].upper()
    return "SLANG_SENSE" if "SLANG" in out else "OTHER_SENSE" if "OTHER" in out else "UNPARSED"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--endpoint", default="http://localhost:8000/v1")
    ap.add_argument("--model", default="nvidia/Llama-3.1-Nemotron-Nano-8B-v1")
    ap.add_argument("--keep-correct-share", type=float, default=0.30)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="default: count rows and estimate tokens only")
    mode.add_argument("--run", action="store_true")
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.inp) if l.strip()]
    # private model: rights kept as provenance only, not a filter (owner decision 2026-10-15)
    rows = [r for r in rows if r.get("contextual_use") and gold_label(r) is not None]
    est_in = sum(len(r["contextual_use"]) // 4 + 40 for r in rows)
    print(json.dumps({"rows": len(rows), "est_input_tokens": est_in, "est_output_tokens": 8 * len(rows), "prompt_sha": PROMPT_SHA}))
    if not a.run:
        return
    key = os.environ.get("AUDIT_API_KEY")  # only for a paid endpoint, after cost approval
    audited = []
    for r in rows:
        g = gold_label(r)
        b = ask(a.endpoint, a.model, PROMPT.format(term=r["term"], ctx=r["contextual_use"]), key)
        audited.append({"record_id": r["record_id"], "split": (r.get("human_ruling") or {}).get("split"),
                        "gold": g, "base": b, "base_correct": b == g, "prompt_sha": PROMPT_SHA})
    final = select_keep(audited, a.keep_correct_share)
    with open(a.out, "w") as fh:
        for r in final:
            fh.write(json.dumps(r) + "\n")
    print(json.dumps({"audited": len(final), "kept": sum(r["keep"] for r in final),
                      "base_acc": sum(r["base_correct"] for r in final) / max(1, len(final))}))


if __name__ == "__main__":
    main()
