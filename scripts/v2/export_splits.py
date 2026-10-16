#!/usr/bin/env python3
"""Export train/val/test JSONL from the PRIVATE local store, deduped on text hash.

Dedup rules (deterministic):
 1. Within a split, keep one row per (content_sha256, term); prefer human-gold, then lowest record_id.
 2. Across splits, each text lives in ONE split, priority test > val > train (protects held-out).
Outputs (private, local_store/export/): {train,val,test}.jsonl (SFT rows), gold_test.jsonl
(prereg_eval.py format: record_id, gold, family), test_manifest.txt + sha256, export_report.json.
SFT row: record_id, split, term, term_family, lineage_family, context, label, label_source, slur_tagged.
"""
import json, os, hashlib, collections, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # 2026-10-16: current tracker ruling_queue, not the vi-data copy
from ruling_queue import split_for, window_excerpt, NON_GOLD_ROW_STATUS
ROOT = os.environ.get("HYPERLEX_LOCAL_STORE", "local_store")  # private store; path set on the operator box
OUT = ROOT + "/export"
PRI = {"test": 0, "val": 1, "train": 2}


def gold(r):
    h = r.get("human_ruling") or {}
    if h.get("row_status") in NON_GOLD_ROW_STATUS:  # spec 009 R = unusable evidence: never gold
        return None
    return h.get("sense") if str(h.get("source", "")).lower() == "human" and h.get("sense") in ("SLANG_SENSE", "OTHER_SENSE") else None


def context_of(r):
    """T026: target-centred window (same width as the ruling queue) instead of the full post."""
    ctx, kind = window_excerpt(r.get("contextual_use") or "", r["term"])
    return ctx, kind


def text_key(r):
    """Dedup key on the exported text itself (case/whitespace-normalised), not only the source post hash:
    identical short excerpts from different posts were surviving as duplicates (readiness check 2026-10-16)."""
    import hashlib as _h
    t = " ".join(str(r.get("contextual_use") or "").lower().split())
    return _h.sha256(t.encode()).hexdigest() if t else r["content_sha256"]


def main(src=ROOT + "/curated_sense_observation.jsonl", out=OUT):
    os.makedirs(out, exist_ok=True)
    rows = [json.loads(l) for l in open(src) if l.strip()]
    rep_ns = sum(1 for r in rows if (r.get("human_ruling") or {}).get("row_status") in NON_GOLD_ROW_STATUS)
    for r in rows:
        r["_split"] = (r.get("human_ruling") or {}).get("split") or split_for(r["term_family"])
    rep = {"input_rows": len(rows), "non_gold_row_status_rows": rep_ns}
    # 1 within-split (text, term)
    best = {}
    for r in sorted(rows, key=lambda r: (gold(r) is None, r["record_id"])):
        k = (r["_split"], text_key(r), r["term"].lower())
        best.setdefault(k, r)
    rows1 = list(best.values()); rep["dropped_exact_dup"] = len(rows) - len(rows1)
    # 2 cross-split
    home = {}
    for r in rows1:
        s = home.get(text_key(r))
        if s is None or PRI[r["_split"]] < PRI[s]:
            home[text_key(r)] = r["_split"]
    rows2 = [r for r in rows1 if home[text_key(r)] == r["_split"]]
    # Opus review PR #31: rows a human judged unusable (R) are not SFT rows either; counted, kept in the store
    rows2_all = rows2
    rows2 = [r for r in rows2 if (r.get("human_ruling") or {}).get("row_status") not in NON_GOLD_ROW_STATUS]
    rep["dropped_non_gold_row_status"] = len(rows2_all) - len(rows2)
    rep["dropped_cross_split"] = len(rows1) - len(rows2)
    by = collections.defaultdict(list)
    for r in rows2:
        g = gold(r)
        ctx, kind = context_of(r)
        h = r.get("human_ruling") or {}
        by[r["_split"]].append({
            "record_id": r["record_id"], "split": r["_split"], "term": r["term"], "term_family": r["term_family"],
            "lineage_family": (r.get("mutation_lineage") or {}).get("lineage_family"),
            "context": ctx, "context_match": kind, "label": g or r["sense_candidate"],
            "use_mention": h.get("use_mention"), "row_status": h.get("row_status"),
            "excerpt_provenance": h.get("excerpt_provenance"),
            "label_source": "human" if g else "model:" + str((r.get("model_proposal") or {}).get("model_or_rule")),
            "slur_tagged": bool((r.get("sensitivity") or {}).get("slur_tagged")), "text_contains_slur": bool((r.get("sensitivity") or {}).get("text_contains_slur"))})
    for s in ("train", "val", "test"):
        with open(f"{out}/{s}.jsonl", "w") as fh:
            for x in sorted(by[s], key=lambda x: x["record_id"]):
                fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    gt = sorted((x for x in by["test"] if x["label_source"] == "human"), key=lambda x: x["record_id"])
    with open(f"{out}/gold_test.jsonl", "w") as fh:
        for x in gt:
            fh.write(json.dumps({"record_id": x["record_id"], "gold": x["label"], "family": x["lineage_family"] or x["term_family"]}) + "\n")
    man = "".join(x["record_id"] + "\n" for x in gt)
    open(f"{out}/test_manifest.txt", "w").write(man)
    rep["test_manifest_sha256"] = hashlib.sha256(man.encode()).hexdigest()
    sha = {r["record_id"]: r["content_sha256"] for r in rows2}
    texts = {s: {sha[x["record_id"]] for x in by[s]} for s in by}  # whole-post hash, not the window
    terms = {s: {x["term"].lower() for x in by[s]} for s in by}
    rep.update({"rows": {s: len(by[s]) for s in by}, "gold_rows": {s: sum(x["label_source"] == "human" for x in by[s]) for s in by},
                "gold_test": len(gt),
                "text_overlap": {"train_test": len(texts["train"] & texts["test"]), "val_test": len(texts["val"] & texts["test"]), "train_val": len(texts["train"] & texts["val"])},
                "term_overlap": {"train_test": len(terms["train"] & terms["test"]), "val_test": len(terms["val"] & terms["test"]), "train_val": len(terms["train"] & terms["val"])},
                "label_by_family": {str(k): dict(v) for k, v in _lab(rows2).items()}})
    json.dump(rep, open(f"{out}/export_report.json", "w"), indent=2)
    print(json.dumps({k: v for k, v in rep.items() if k != "label_by_family"}, indent=2))


def _lab(rows):
    c = collections.defaultdict(collections.Counter)
    for r in rows:
        c[(r.get("mutation_lineage") or {}).get("lineage_family")][gold(r) or r["sense_candidate"]] += 1
    return c


if __name__ == "__main__":
    main()
