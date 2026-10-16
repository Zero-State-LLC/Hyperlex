# Tasks 008: Lexical emergence

Status: DRAFT / SHADOW.

**Legend**

- `[x]` means done in this docs PR.
- `[ ]` means future work. It needs an operator-accepted implement cycle.
- `[gate]` means a human or operator decision.

**Rules**

- Each future task is test-first and goes in a `hyperlex.analysis.*` module, which is named at implement.
- No CLI before the library and its tests exist.
- Gate failure means stop and open a `bug` issue. Tests are never weakened to pass.

## Docs PR (this PR)

- [x] **T001** `spec.md`: doctrine change, FR-001–FR-029, CR-1–CR-12; Danny decisions recorded in §14 (2026-10-15 9:52 PM PT).
- [x] **T002** `plan.md`: phases E0–E5, stages S1–S4, first-experiment prereg sketch.
- [x] **T003** `data-model.md`: entities, store column mapping, -slop rule.
- [x] **T004** `contracts/occurrence_record.v1.schema.json`.
- [x] **T005** `contracts/candidate_hypothesis.v1.schema.json`.
- [x] **T006** `contracts/emergence_evidence.v1.schema.json`: `verified` const false, `promotion` const `SHADOW_ONLY`, guard flags as measured features.
- [x] **T007** `contracts/forecast_receipt.v1.schema.json`: brier null unless an eligible class has an operator TRUE/FALSE settlement.
- [x] **T008** `research.md`: C1–C3 verified, with everything else marked UNVERIFIED.
- [x] **T009** `intent/2026-10-15-lexical-emergence.md`, status draft (awaiting Danny).
- [x] **T009a** Danny answered Q2–Q6 on PR #28 (2026-10-15 9:52 PM PT); spec, data model, contracts and intent updated.
- [ ] **T010** `[gate]` Danny accepts the intent and approves the `specs/index.yaml` 008 entry.

## E0: Preserve every valid first occurrence

- [ ] **T011** Contract tests (SC-003):
  - All 4 schemas validate against the 2020-12 meta-schema.
  - Synthetic fixtures pass or fail as expected.
  - Non-null `brier` on an unsettled receipt fails.
  - `verified: true` fails.
  - A censored receipt with an `outcome_value` fails.
- [ ] **T012** Canonical `record_hash` function, with a golden-vector test on synthetic records.
- [ ] **T013** Mapper from private store columns to OccurrenceRecord (data-model §4).
  - Tests cover: `contextual_use` is never copied, `surface` is null for overlay members, and `legacy.*` is preserved.
- [ ] **T014** No-filter test: hapax, single-day, single-author, dormant, REJECTED, and rights-restricted rows are all written. The drop count is 0.
- [ ] **T015** Dedup marking test: exact and near duplicates are marked and not deleted. The earliest `observed_at` is canonical.
- [ ] **T016** DISCOVERY_HIT test: it never increments `occurrence_count` and yields `NOT_ATTESTED` only.
- [ ] **T017** Replay test (SC-001): replaying from source reproduces 100% identical `record_hash`. A correction creates a superseding record, and the old hash stays unchanged.
- [ ] **T018** Export vs store check (CR-6): find which copy `export_splits.py` keeps per `content_sha256`, and report any first-occurrence timestamp mismatch. Read-only. Export is not changed.
- [ ] **T019** VERDICT-RULES v1.4 regression (SC-002): verdicts and guard flags for all existing terms are identical before and after.
- [ ] **T020** Safety tests:
  - Overlay members get an opaque `lex-h-` id.
  - Hashes are keyed.
  - `restricted_intent_suspected` leads to hash and tags only.
- [ ] **T021** Diff scan (SC-006): no post text, raw handles, or slur-list terms. The scan runs against the private list locally and the list is never committed.
- [ ] **T022** `[gate]` E0 gate review (plan §1 E0 a–d).

## E1: Registry and provisional senses

- [ ] **T023** Stable `candidate_id` assignment. Test: every OBSERVED occurrence maps to exactly 1 candidate, and ids are stable across replay.
- [ ] **T024** Legacy ruling copy: S/O/U/R are copied verbatim. Historical R (through 2026-10-15) = REJECTED and stays out of cohorts. Test: no historical ruling changes meaning. New rulings use R (target absent → occurrence `TARGET_ABSENT`, extraction repair; amended 2026-10-16 by spec 009 Q5) or H (not yet established → stays `OBSERVED`).
- [ ] **T025** Sense hypotheses: null gloss is allowed, competing hypotheses are kept, and labels are INFERRED, OBSERVED, or SPECULATIVE per FR-010.
- [ ] **T026** -slop non-identity test: related candidates never pool counts, and `merged_into` is only set by a MergeRecord fixture.
- [ ] **T027** Oct-13 holds:
  - goreslop becomes `OBSERVED` only after T017 passes, and uses the overlay ref only.
  - The other 8 stay `NOT_ATTESTED` (Danny Q5).
- [ ] **T028** S1 characterization using the SHADOW trunk from spec 007. Outputs are INFERRED or SPECULATIVE only, and there is a no-authoritative-label test.

## E2: Temporal recurrence and cohorts

- [ ] **T029** As-of temporal features. Leakage test: no input after `as_of`.
- [ ] **T030** Coverage report per source and week, including author and community coverage. `NOT_COMPUTABLE` where columns are missing (CR-7).
- [ ] **T031** Censoring tests: data end and coverage gap give censored, never 0.
- [ ] **T032** Guard features as measured features. Test: they equal the qualification guards on the same window.
- [ ] **T033** Power check: count novel first occurrences and decide whether the experiment is feasible.

## E3: Baseline forecasting

Prerequisite: T038 (author and community backfill, listed under E4) runs ahead of E3 because the E3 target needs author pseudonyms. It is already done.

- [ ] **T034** `[gate]` Freeze the prereg (plan §4) and the cohort manifest SHA-256 before any test load.
- [ ] **T035** Three baselines plus S2 logistic and survival models, tuned on validation only.
- [ ] **T036** Write ForecastReceipts. Test: all `brier` fields are null.
- [ ] **T037** Single final run. Publish results, including negative ones, and report any rerun.

## E4: Diffusion and semantic stability

- [x] **T038** `[gate]` Owner-approved backfill of `author_id` (HMAC, CR-7) and two-level `community` into the private store (approved 2026-10-15 9:52 PM PT; private-store operation, no repo data). Coverage recorded in the PR thread.
- [ ] **T038a** Coverage test: report author and community coverage per platform; within-platform and cross-platform diffusion return `NOT_COMPUTABLE` below the coverage floor.
- [ ] **T039** S3 and S4, run only where coverage meets the preregistered minimum. Must beat morphology+frequency.

## E5: Abraxas evidence integration

- [ ] **T040** Export-only compat shape for EmergenceEvidence. Static test: no Abraxas import.
- [ ] **T041** Payload test: 100% of payloads carry `verified: false` and `promotion: SHADOW_ONLY`.
- [ ] **T042** `[gate]` Operator decision on landing contracts in `schemas/`, plus `API_EXTENDED` symbols.
