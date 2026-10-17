# Shadow near-duplicate checker

Opt-in guard for near-duplicate text between train rows and val or holdout texts. It is off unless `HLX_NEARDUP_GUARD=1`. It is not wired into `train.py`. It is not a Hermes skill command: `SKILL.md` names `scripts/hyperlex.py` and does not name this module.

## Checker

From the repo root:

```bash
python -m scripts.shadow.hyperlexical.neardup_guard --train T --val V [--holdout-texts H] [--threshold X]
```

`T` and `V` are JSONL files of objects with a `text` field. `H` is JSONL or a JSON list of texts. The threshold is a Jaccard cutoff in `(0, 1]`, default `0.7`. The process exits `2` when any pair is at or above the threshold, and `0` when none are.

Similarity is character 3-5-gram Jaccard on `heldout_census.normalize_group_text`. The candidate index stores 3-grams, 4-grams, and 5-grams, so a pair that shares only a lower-order gram is still scored. A text shorter than 5 characters is compared with a longer text when they share a 3-gram or a 4-gram. A text shorter than 3 characters has an empty gram set and Jaccard 0.

## Admission

When `HLX_NEARDUP_GUARD=1`, `enforce_from_env` requires `HLX_NEARDUP_HOLDOUT_TEXTS`. A missing file, a bad threshold, or any pair at or above the threshold refuses with `ADMISSION FAIL`. `HLX_NEARDUP_MODE=drop` drops the offending train rows and writes a receipt instead. `HLX_NEARDUP_THRESHOLD` overrides the default `0.7`.

This is a future prereg item. In-flight training and prereg files are untouched.
