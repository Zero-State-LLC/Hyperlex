---
id: intent-2026-10-12-neardup-guard
status: accepted
depends_on: ["007"]
---

# Intent

## Problem

Train versus val, and train versus holdout, can share near-duplicate text. The holdout guard matches exact normalized text only. Nothing fails closed on a high character n-gram Jaccard.

## Proposed outcome

What this branch already does:

- `scripts/shadow/hyperlexical/neardup_guard.py`: character 3-5-gram Jaccard, with an inverted index over 3-grams, 4-grams, and 5-grams.
- Off unless `HLX_NEARDUP_GUARD=1`. When enabled, a missing holdout file, a bad threshold, or any pair at or above `HLX_NEARDUP_THRESHOLD` (default 0.7) refuses with `ADMISSION FAIL`. `HLX_NEARDUP_MODE=drop` drops the offending train rows and writes a receipt.
- A shadow checker, documented in `scripts/shadow/hyperlexical/README.md`:

  `python -m scripts.shadow.hyperlexical.neardup_guard --train T --val V [--holdout-texts H] [--threshold X]`

  It exits 2 when any pair is at or above the threshold. This is not a `SKILL.md` command.

Out of scope: wiring the guard into `train.py`, prereg files, holdout manifests, in-flight runs, and a `SKILL.md` rewrite.

## Affected users / systems

- shadow training admission, only when the env flag is set
- the shadow checker above
- holdout-guard CI, which runs `tests/shadow/test_neardup_guard.py`

## Constraints / non-goals

- `SKILL.md` stays the Hermes command contract. The checker is a shadow module, not a new skill command.
- Not called from `train.py`. In-flight training is unchanged.
- Brier stays null until an operator settles an outcome.
- No Abraxas import. No live ingest. No holdout-manifest edits.

## Open questions

None for this guard. Danny accepted the harness-learning batch on 2026-10-12 (P0, 2:48 AM PT). This is item P5 of that batch.

## Verified / assumed claims

| Claim | Label | Basis |
|---|---|---|
| The guard is off unless `HLX_NEARDUP_GUARD=1` | `OBSERVED` | `neardup_guard.enforce_from_env` |
| The checker command is the one named in the PR #22 body | `OBSERVED` | PR #22 body; `scripts/shadow/hyperlexical/README.md` |
| Danny accepted this harness-learning batch on 2026-10-12 | `OBSERVED` | PR #20 body ("Danny yes 2026-10-12 2:48 AM PT"); owner instruction 2026-10-17 to fix these PRs and then merge |
| `SKILL.md` does not name this checker | `OBSERVED` | `SKILL.md` command list |

## Author / date

- Author: recorded for the existing guard after Danny's 2026-10-12 yes
- Date: 2026-10-12 (recorded 2026-10-17)
