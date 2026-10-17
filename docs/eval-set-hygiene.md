# Eval-set hygiene: feedback / dev / held-out (2026-10-12)

Docs only. No training, prereg, or guard behavior changes. Prompted by arXiv 2609.35738 ("Harness Learning Enables Generalizable Test-Time Adaptation", §4.1 Question sets). That section uses three question sets: Q_fb (feedback the learner sees), Q_score (selects candidates), and Q_eval (held-out performance). Evaluation questions are disjoint from questions used for feedback or candidate selection. Feedback and scoring sets may coincide. Hyperlex still keeps train, val, and sealed holdout separate; that split is this repo's protocol, not a requirement that all three paper sets be disjoint.

## How Hyperlex maps to the three sets

| Paper set | Hyperlex set | Where it is enforced |
|---|---|---|
| Q_fb (feedback) | `classify_train`, `unbind_train` | training loop only |
| Q_score (dev selection) | `classify_val`, `unbind_val`; checkpoint picked by `HLX_SELECT_METRIC` on val (strict `>`) | rc4 prereg: "never picked by held-out score" |
| Q_eval (held out) | sealed holdout manifests (classify-v1, v1b; v2 is SCORED_SPENT, non-gating) | `scripts/shadow/hyperlexical/holdout_guard.py` (PR #120): drops holdout rows by row id and by sha256 of `normalize_group_text`, from all four train/val keys, before training and selection; `require_holdout_for_training` fails closed unless `HLX_ALLOW_NO_HOLDOUT` |

## Verified 2026-10-12 PT (archived scrimshawlife-ctrl/Hyperlex, origin/main ad4075b)

- `tests/shadow/test_hyperlexical_holdout_disjoint.py`, `tests/shadow/test_hyperlexical_holdout_guard.py`, `tests/heldout/`: 41 passed.
- Held-out sets are frozen and read-only. Final reported comparisons use held-out sets. Validation still compares candidates: `HLX_SELECT_METRIC` picks a checkpoint on val (strict `>`), and a checkpoint is "never picked by held-out score" (rc4 prereg).

## Known gaps (not fixed here)

0. **This repo (Zero-State-LLC/Hyperlex @ 7721220) does not contain the holdout guard.** `holdout_guard.py`, `holdout_eligibility.py`, `heldout_census.py` and their tests exist only in the archived scrimshawlife-ctrl/Hyperlex (PR #120). Any training run from this repo has no automated holdout filter. Porting the guard is a separate decision.

1. Train vs val near-duplicates are not blocked by a guard. rc4 handles this with a one-off hygiene split (`HLX_CLASSIFY_SPLIT_FILE`, cluster-to-val), and `force_train_overlap` counts and logs only. Measured on rc3: 0.6% exact and 9.1% near-dup (char 3-5 J >= 0.7) of val rows.
2. The holdout guard matches exact normalized text, not near-duplicates of holdout rows. rc4 removed 10 train rows near holdout text by a separate pass.
3. Spending a holdout (UNSCORED_SEALED -> SCORED_SPENT) is the only thing stopping repeated peeking; any auto-tuning loop must score candidates on val only and touch a sealed holdout once per prereg.

Rule (unchanged): the holdout is never trained on and never used for selection.
