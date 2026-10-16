#!/usr/bin/env python3
"""G4 BASE audit (draft). Reads private curated JSONL, queries an OpenAI-compatible endpoint
(vLLM on DGX Spark by default), writes private audit JSONL. Never prints post text.

  python scripts/v2/base_audit.py --in /path/private/curated_sense_observation.jsonl \
      --out /path/private/audit_v1.jsonl --endpoint http://spark:8000/v1 --dry-run

--dry-run (default) only counts rows and estimates tokens; --run is required to call the model.
"""
import argparse, hashlib, json, os, sys, urllib.request

PROMPT = ("Term: {term}\nContext: {ctx}\n"
          "Is the term used in its slang sense here? Answer SLANG_SENSE or OTHER_SENSE only.")
PROMPT_SHA = hashlib.sha256(PROMPT.encode()).hexdigest()[:12]


def gold_label(r):
    h = r.get("human_ruling") or {}
    return h.get("sense") if h.get("sense") in ("SLANG_SENSE", "OTHER_SENSE") else r.get("sense_candidate")


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
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.inp) if l.strip()]
    rows = [r for r in rows if r.get("contextual_use") and (r.get("rights") or {}).get("redistribution") == "allowed_internal"]
    est_in = sum(len(r["contextual_use"]) // 4 + 40 for r in rows)
    print(json.dumps({"rows": len(rows), "est_input_tokens": est_in, "est_output_tokens": 8 * len(rows), "prompt_sha": PROMPT_SHA}))
    if not a.run:
        return
    key = os.environ.get("AUDIT_API_KEY")  # only for a paid endpoint, after cost approval
    with open(a.out, "w") as fh:
        for r in rows:
            g = gold_label(r)
            b = ask(a.endpoint, a.model, PROMPT.format(term=r["term"], ctx=r["contextual_use"]), key)
            fh.write(json.dumps({"record_id": r["record_id"], "gold": g, "base": b, "base_correct": b == g,
                                 "prompt_sha": PROMPT_SHA}) + "\n")
    # keep/drop selection is applied in a second pass so the correct-share cap is deterministic (seeded by record_id)


if __name__ == "__main__":
    main()
