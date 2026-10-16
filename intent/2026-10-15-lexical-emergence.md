---
id: intent-008-lexical-emergence
status: draft (awaiting Danny)
depends_on: ["constitution", "007"]
---

# Intent

## Problem

Archived vernacular doctrine (VERDICT-RULES v1.4) affects single-use and early expressions in three ways:

- Guard flags (`SINGLE_BURST`, `ONE_AUTHOR_DEPENDENCE`, `BOTLIKE_REPETITION`, `DORMANT_OR_UNDATED`) cap them at OBSERVE or HOLD.
- Ruling code R writes `rejected`.
- Export dedups on text hash.

As a result, first occurrences of new words can drop out of later measurement. Hyperlex cannot learn which innovations spread if it does not keep the ones that never did.

Brief, Danny 2026-10-15 21:11 PT: move to "every valid lexical innovation is eligible for observation from its first attested occurrence".

Steering, 21:13 PT: research each conflict and integrate it.

## Proposed outcome

Spec 008 docs PR:

- `spec.md`, `plan.md`, `data-model.md`, `research.md`, `tasks.md`
- four draft contracts:
  - OccurrenceRecord
  - CandidateHypothesis
  - EmergenceEvidence
  - ForecastReceipt

The PR covers:

- Observation is separated from qualification and promotion.
- Guard flags become measured features. They still block PASS.
- Dormancy, R, and HOLD never delete.
- Forecasts are SPECULATIVE receipts with mandatory right-censoring.
- A preregistered first experiment: independent 30-day recurrence vs a morphology+frequency baseline.
- Phases E0 to E5 with gates.

Out of scope:

- implementation code
- changes to VERDICT-RULES v1.4, `ruling_queue.py`, `export_splits.py`, `forecast.v1`, or API_V1
- landing schemas in `schemas/`
- the index entry
- reviving the "V6 classifier"

## Affected users / systems

- operators
- private store `slang_v1.sqlite3`
- the ruling queue, which is read-only here
- training export, which is read-only here
- the future `hyperlex.analysis.*` module
- the SHADOW ModernBERT trunk (spec 007)
- downstream consumers Abraxas (export-only), Noesis, and Trutina, with interfaces UNVERIFIED

## Constraints / non-goals

- Settled Brier only. All `brier` fields are null unless an eligible class has an operator TRUE/FALSE settlement.
- Every claim is labelled OBSERVED, INFERRED, SPECULATIVE, or NOT_COMPUTABLE.
- No Abraxas import.
- `verified: false` and `promotion: SHADOW_ONLY` are consts.
- Receipts and record hashes are frozen. Corrections supersede.
- No post text, no raw handles, and no slur-list terms in the repo. Overlay members are referenced only.
- Owner-gated: live ingest or re-ingest, settlement, schema landing, hub publish, legal, and spend.
- Historical R rulings stay REJECTED (Danny, 2026-10-15); this work does not reinterpret them.

## Open questions

Danny decides all of these. They are spec §14.

| # | Question |
|---|---|
| (resolved) | `SHADOW_INSTRUMENT_ONLY` and V6: resolved from argotide `docs/EVIDENCE.md` (see spec CR-8). |
| Q2 | Answered YES: HMAC author id + community re-ingest (spec CR-7). |
| Q3 | Answered: Oct-13 R = REJECTED; R/H split prospective only (CR-5). |
| Q5 | Answered: 8 holds stay NOT_ATTESTED. |
| Q6 | Answered: two levels, within-platform and cross-platform (CR-7). |

## Verified / assumed claims

| Claim | Label | Basis |
|---|---|---|
| Single-use rejection effect lives in VERDICT-RULES v1.4, not on main | `OBSERVED` | F1 repo search; Hyperlex-archive d43a44a, PR #124 |
| Store lacked author and community columns before the approved 2026-10-15 backfill | `OBSERVED` | F3 schema of `slang_v1.sqlite3` |
| R writes status `rejected` | `OBSERVED` | F4 `ruling_queue.py` |
| goreslop has 10 rows; the other 8 holds have 0 | `OBSERVED` | F6 private store query |
| Genuineness of occurrences for the 8 holds | `NOT_COMPUTABLE` | no attested rows; discovery hits only |
| Bursts and never-spread terms are needed as data | `INFERRED` | C1 and C2 (research.md) |
| Hyperlex beats morphology+frequency at 30-day recurrence | `NOT_COMPUTABLE` | experiment not run; needs author pseudonyms |
| Noesis and Trutina interfaces | `NOT_COMPUTABLE` | not defined on main |

## Author / date

- Author: agent draft (Claude Opus) for Danny, from brief 2026-10-15 21:11 PT
- Date: 2026-10-15
