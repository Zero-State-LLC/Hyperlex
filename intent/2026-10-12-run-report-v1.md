---
id: intent-2026-10-12-run-report-v1
status: accepted
depends_on: ["007"]
---

# Intent

## Problem

The archived holdout guard and the eval scripts that sit on it were not in this checkout. A training or eval run here could not fail closed on a sealed holdout, and eval numbers had no separate count of predictions that parse to a known family.

## Proposed outcome

What this branch already does:

- Port the archived holdout guard, its training entrypoints, and `scripts/shadow/recoverable_structure/` from scrimshawlife-ctrl/Hyperlex @ ad4075b, so a clean checkout can import the training export and `eval_unbind`.
- Add `run_report.v1` (`scripts/shadow/hyperlexical/run_report.py`). It writes only when `HLX_RUN_REPORT` is set. It records status, inputs without row text, counts, scores, validity, warnings, and errors. It does not change eval numbers, stdout, or exit codes. A failed write does not raise.
- Wire that report into `eval_unbind.main` and `eval_classify.main`.
- Count validity from the predictions actually scored, separate from the task score.

Out of scope: prereg files, holdout manifests, in-flight runs, operator settlement, live ingest, a `SKILL.md` command change, and official Hermes hub publish.

## Affected users / systems

- shadow training entrypoints and holdout admission
- `eval_classify` and `eval_unbind` when `HLX_RUN_REPORT` is set
- holdout-guard CI

## Constraints / non-goals

- `SKILL.md` stays the Hermes command contract. This work does not add a skill command.
- Brier stays null until an operator settles an outcome.
- Phase 5 stays SPECULATIVE.
- No Abraxas import. The ported probe keeps its existing receipt schema string; it does not import Abraxas.
- Fail closed on a missing or malformed holdout manifest.
- Do not rewrite historical receipts.

## Open questions

None for this port. Danny accepted the harness-learning batch on 2026-10-12 (P0, 2:48 AM PT), including landing this implementation after the review bugs were fixed.

## Verified / assumed claims

| Claim | Label | Basis |
|---|---|---|
| Archived source of the port is scrimshawlife-ctrl/Hyperlex @ ad4075b | `OBSERVED` | `scripts/shadow/hyperlexical/PORTED.md` |
| `run_report.v1` is off unless `HLX_RUN_REPORT` is set | `OBSERVED` | `scripts/shadow/hyperlexical/run_report.py` |
| Danny accepted this harness-learning batch on 2026-10-12 | `OBSERVED` | PR #20 body ("Danny yes 2026-10-12 2:48 AM PT"); owner instruction 2026-10-17 to fix these PRs and then merge |

## Author / date

- Author: recorded for the existing port after Danny's 2026-10-12 yes
- Date: 2026-10-12 (recorded 2026-10-17)
