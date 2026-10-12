"""Fail-closed near-duplicate guard between train rows and val/holdout texts.

No-op unless HLX_NEARDUP_GUARD=1.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Mapping, Sequence

from .heldout_census import normalize_group_text

DEFAULT_THRESHOLD = 0.7
NGRAM_RANGE = (3, 5)
MIN_N, MAX_N = NGRAM_RANGE
SCHEMA = "hyperlex.neardup_guard.v1"


def _grams_from_norm(norm: str, lo: int = MIN_N, hi: int = MAX_N) -> frozenset[str]:
    if len(norm) < lo:
        return frozenset()
    out: set[str] = set()
    top = min(hi, len(norm))
    for n in range(lo, top + 1):
        for i in range(len(norm) - n + 1):
            out.add(norm[i : i + n])
    return frozenset(out)


def char_ngrams(text: str) -> frozenset[str]:
    """All char n-grams (n in 3..5) of the normalized text."""
    return _grams_from_norm(normalize_group_text(text or ""))


def jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    """Jaccard similarity; 0.0 when either side is empty."""
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    return inter / len(a | b)


def find_near_duplicates(
    train_texts: Sequence[str],
    other_texts: Sequence[str],
    threshold: float,
) -> list[dict]:
    """All (i, j) pairs with jaccard(train[i], other[j]) >= threshold."""
    train_norms = [normalize_group_text(t or "") for t in train_texts]
    other_norms = [normalize_group_text(t or "") for t in other_texts]

    train_5 = [_grams_from_norm(s, 5, 5) for s in train_norms]
    other_5 = [_grams_from_norm(s, 5, 5) for s in other_norms]

    full_cache: dict[tuple[str, int], frozenset[str]] = {}

    def full(side: str, idx: int) -> frozenset[str]:
        key = (side, idx)
        got = full_cache.get(key)
        if got is None:
            norm = train_norms[idx] if side == "t" else other_norms[idx]
            got = _grams_from_norm(norm)
            full_cache[key] = got
        return got

    inv: dict[str, list[int]] = {}
    short_others: list[int] = []
    for j, g5 in enumerate(other_5):
        if g5:
            for g in g5:
                inv.setdefault(g, []).append(j)
        else:
            short_others.append(j)

    results: list[dict] = []
    for i, tg5 in enumerate(train_5):
        if tg5:
            cands: set[int] = set()
            for g in tg5:
                cl = inv.get(g)
                if cl:
                    cands.update(cl)
            if not cands:
                continue
            ti = full("t", i)
            for j in sorted(cands):
                x = jaccard(ti, full("o", j))
                if x >= threshold:
                    results.append(
                        {"train_index": i, "other_index": j, "jaccard": round(x, 4)}
                    )
        elif short_others:
            ti = full("t", i)
            for j in short_others:
                x = jaccard(ti, full("o", j))
                if x >= threshold:
                    results.append(
                        {"train_index": i, "other_index": j, "jaccard": round(x, 4)}
                    )

    results.sort(key=lambda r: (r["train_index"], r["other_index"]))
    return results


def _extract_text(item, where: str) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict) and "text" in item:
        return item["text"]
    raise SystemExit(f"REFUSE: bad holdout entry in {where}")


def load_holdout_texts(path: str) -> list[str]:
    """Load texts from JSONL (objects with 'text' or strings) or a JSON list."""
    p = Path(path)
    if not p.is_file():
        raise SystemExit(f"REFUSE: holdout texts file not found: {path}")
    try:
        raw = p.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"REFUSE: cannot read holdout texts file {path}: {exc}")
    stripped = raw.strip()
    if not stripped:
        raise SystemExit(f"REFUSE: holdout texts file is empty: {path}")

    texts: list[str] = []
    parsed_list = None
    try:
        parsed_list = json.loads(stripped)
    except json.JSONDecodeError:
        parsed_list = None

    if isinstance(parsed_list, list):
        for item in parsed_list:
            texts.append(_extract_text(item, path))
    else:
        for lineno, line in enumerate(raw.splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"REFUSE: bad JSONL {path}:{lineno}: {exc}")
            texts.append(_extract_text(item, f"{path}:{lineno}"))

    if not texts:
        raise SystemExit(f"REFUSE: holdout texts file has no texts: {path}")
    return texts


def config_from_env() -> dict:
    enabled = os.environ.get("HLX_NEARDUP_GUARD", "0") == "1"

    raw_thr = os.environ.get("HLX_NEARDUP_THRESHOLD")
    if raw_thr is None or raw_thr == "":
        threshold = DEFAULT_THRESHOLD
    else:
        try:
            threshold = float(raw_thr)
        except ValueError:
            raise SystemExit(
                f"REFUSE: HLX_NEARDUP_THRESHOLD not a float: {raw_thr!r}"
            )
        if not (0.0 < threshold <= 1.0):
            raise SystemExit(
                f"REFUSE: HLX_NEARDUP_THRESHOLD must be in (0,1]: {threshold}"
            )

    mode = os.environ.get("HLX_NEARDUP_MODE", "fail")
    if mode not in ("fail", "drop"):
        raise SystemExit(
            f"REFUSE: HLX_NEARDUP_MODE must be 'fail' or 'drop': {mode!r}"
        )

    holdout_texts_path = os.environ.get("HLX_NEARDUP_HOLDOUT_TEXTS") or None
    return {
        "enabled": enabled,
        "threshold": threshold,
        "mode": mode,
        "holdout_texts_path": holdout_texts_path,
    }


def _texts_of(rows: Sequence[dict]) -> list[str]:
    out: list[str] = []
    for r in rows:
        if isinstance(r, dict):
            out.append(r.get("text", "") or "")
        else:
            out.append("")
    return out


def enforce_from_env(
    train_sets: Mapping[str, list[dict]],
    val_sets: Mapping[str, list[dict]],
) -> tuple[dict[str, list[dict]], dict | None]:
    """Apply guard. No-op unless HLX_NEARDUP_GUARD=1."""
    cfg = config_from_env()
    if not cfg["enabled"]:
        return (dict(train_sets), None)

    if cfg["holdout_texts_path"] is None:
        raise SystemExit(
            "REFUSE: HLX_NEARDUP_GUARD=1 needs HLX_NEARDUP_HOLDOUT_TEXTS"
        )

    threshold = cfg["threshold"]
    mode = cfg["mode"]
    holdout_texts = load_holdout_texts(cfg["holdout_texts_path"])

    new_train: dict[str, list[dict]] = {}
    per_set: dict[str, dict] = {}
    total_v = 0
    total_h = 0

    for k in train_sets:
        train_rows = list(train_sets[k])
        train_texts = _texts_of(train_rows)
        val_rows = list(val_sets.get(k, []) or [])
        val_texts = _texts_of(val_rows)

        pairs_v = find_near_duplicates(train_texts, val_texts, threshold)
        pairs_h = find_near_duplicates(train_texts, holdout_texts, threshold)

        if mode == "drop":
            drop_idx = {p["train_index"] for p in pairs_v} | {
                p["train_index"] for p in pairs_h
            }
            new_train[k] = [
                r for idx, r in enumerate(train_rows) if idx not in drop_idx
            ]
            dropped = len(drop_idx)
        else:
            new_train[k] = list(train_rows)
            dropped = 0

        examples = (pairs_v + pairs_h)[:5]
        per_set[k] = {
            "train_vs_val_pairs": len(pairs_v),
            "train_vs_holdout_pairs": len(pairs_h),
            "train_rows_dropped": dropped,
            "examples": examples,
        }
        total_v += len(pairs_v)
        total_h += len(pairs_h)

    if mode == "fail" and (total_v + total_h) > 0:
        raise SystemExit(
            "ADMISSION FAIL: near-duplicate rows detected: "
            f"train_vs_val={total_v} train_vs_holdout={total_h} "
            f"(threshold={threshold}, mode=fail)"
        )

    receipt = {
        "schema": SCHEMA,
        "threshold": threshold,
        "mode": mode,
        "ngram_range": [MIN_N, MAX_N],
        "per_set": per_set,
    }
    return new_train, receipt


def _read_rows(path: str) -> list[dict]:
    p = Path(path)
    if not p.is_file():
        raise SystemExit(f"REFUSE: file not found: {path}")
    rows: list[dict] = []
    for lineno, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"REFUSE: bad JSONL {path}:{lineno}: {exc}")
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="hyperlexical.neardup_guard")
    ap.add_argument("--train", required=True)
    ap.add_argument("--val", required=True)
    ap.add_argument("--holdout-texts", default=None)
    ap.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    args = ap.parse_args(argv)

    if not (0.0 < args.threshold <= 1.0):
        raise SystemExit(
            f"REFUSE: threshold must be in (0,1]: {args.threshold}"
        )

    train_rows = _read_rows(args.train)
    val_rows = _read_rows(args.val)
    train_texts = _texts_of(train_rows)
    val_texts = _texts_of(val_rows)
    holdout_texts = load_holdout_texts(args.holdout_texts) if args.holdout_texts else []

    pairs_v = find_near_duplicates(train_texts, val_texts, args.threshold)
    pairs_h = (
        find_near_duplicates(train_texts, holdout_texts, args.threshold)
        if holdout_texts
        else []
    )

    report = {
        "all": {
            "train_vs_val_pairs": len(pairs_v),
            "train_vs_holdout_pairs": len(pairs_h),
            "train_rows_dropped": 0,
            "examples": (pairs_v + pairs_h)[:5],
        }
    }
    print(json.dumps(report, indent=2))
    return 2 if (pairs_v or pairs_h) else 0


if __name__ == "__main__":
    sys.exit(main())
