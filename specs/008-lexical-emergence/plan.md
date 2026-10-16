# Plan 008: Lexical emergence

Status: DRAFT / SHADOW. This PR contains docs and contracts only. Every implement step is a future, operator-accepted cycle.

## 1. Phases and gates

Each phase must pass its gate before the next starts. Any gate failure stops work and opens a bounded `bug` issue (AGENTS.md escalation). Tests are not weakened to pass.

| Phase | Scope | Gate (all required) |
|---|---|---|
| **E0** Preserve every valid first occurrence | OccurrenceRecord v1 writer in the private store; replay from source; dedup marking without deletion | (a) Replay reproduces identical `record_hash` for 100% of records. (b) Zero records dropped by count, recency, dedup, or rights. (c) VERDICT-RULES v1.4 verdicts and guard flags for existing terms are unchanged. (d) Discovery hits are never counted as attested. |
| **E1** Registry and provisional senses | Stable `candidate_id`; CandidateHypothesis revisions; competing sense hypotheses; typed relations; S1 characterization | (a) Every OBSERVED occurrence maps to exactly one candidate. (b) No forced gloss: null is allowed and competing hypotheses are kept. (c) The -slop non-identity test passes. (d) Overlay members have null surface and an opaque id. |
| **E2** Temporal recurrence and cohorts | As-of temporal features; dormancy over covered time; censoring; coverage report | (a) Coverage report per source and week, including author and community coverage. (b) Censoring unit tests: data end and coverage gaps give censored, never negative. (c) Guard features match the qualification guards when both are computed on the same window. |
| **E3** Baseline forecasting | The three baselines and S2; ForecastReceipts; frozen chronological eval | (a) Preregistration frozen and SHA-256 hashed before test load. (b) Test labels loaded once by a final run, and any rerun reported. (c) All `brier` fields null. (d) Results published, including negative ones. |
| **E4** Diffusion and semantic stability | S3 and S4 | (a) Beats the morphology+frequency baseline on held-out test under the preregistered criterion. (b) Diffusion targets run only where author and community coverage meets the preregistered minimum. Otherwise they are `NOT_COMPUTABLE`. |
| **E5** Abraxas evidence integration | EmergenceEvidence via an export-only compat shape | (a) No Abraxas import (static check). (b) `verified:false` and `promotion:SHADOW_ONLY` on 100% of payloads. (c) Independent verification is done on the Abraxas side. (d) Operator gate before any schema lands in `schemas/`. |

## 2. Model stages

| Stage | Phase | What | Not allowed |
|---|---|---|---|
| **S1** zero-shot characterization | E1 | ModernBERT representation (SHADOW trunk, spec 007 / `docs/shadow-hyperlexical.md`), char and subword features, morphology and formation hypothesis, context features, nearest neighbors | No authoritative label. Output is INFERRED or SPECULATIVE only. |
| **S2** recurrence baselines | E3 | Regularized logistic regression; survival model for time to recurrence; as-of features only | No features after `prediction_ts` |
| **S3** diffusion | E4 | Distinct-author and new-community adoption | No silent author or community proxy |
| **S4** semantic evolution | E4 | Sense stability; homographs, quotes, sarcasm, names, compositional uses | No forced meaning. No merge by similarity. |

## 3. Data flow

1. The private store (`slang_v1.sqlite3` and future re-ingest) produces OccurrenceRecords. They are immutable.
2. Occurrences feed the CandidateHypothesis registry. Revisions are append-only.
3. As-of features at time T produce EmergenceEvidence (SHADOW).
4. Frozen features produce a ForecastReceipt. Its `brier` stays null.
5. A later outcome block is written. A settlement is added only if the operator makes the class eligible.
6. Qualification (VERDICT-RULES v1.4) runs alongside, unchanged.

## 4. First experiment: preregistration sketch

**Question (brief):** Can Hyperlex predict independent recurrence within 30 days from first observed occurrence better than a morphology-and-frequency baseline?

Freeze this section, plus the cohort manifest SHA-256, before any test load. The same discipline as `docs/v2/G5_PREREG_EVAL.md` applies.

### Unit and anchor

- The unit is a candidate with `lexical_status = OBSERVED`.
- `t0` is the earliest attested `observed_at` among non-duplicate occurrences.
- Novelty: the candidate has no attested occurrence in a preregistered lookback before `t0`. Candidates without full lookback coverage are excluded and counted.

### Prediction time and features

- `prediction_ts = t0 + Δ`. The proposal is Δ = 24 h, fixed at freeze.
- Features use data at or before `prediction_ts` only, from a frozen snapshot with a recorded hash.

### Target

- Y = 1 if at least one attested occurrence falls in `(prediction_ts, t0 + 30 d]` and meets all of these:
  - it has an author pseudonym different from every author pseudonym seen up to `prediction_ts`
  - it is not an exact duplicate of earlier text
  - it is not in the same near-duplicate cluster as earlier text
- Y = 0 otherwise, if the window is fully covered.
- If author pseudonym coverage is below the preregistered minimum, the target is `NOT_COMPUTABLE`. The experiment does not run. There is no proxy (spec CR-7).

### Censoring

- The window is right-censored, with no 0 label, if either of these holds:
  - `t0 + 30 d` passes the data end
  - an ingest coverage gap overlaps the window
- Censored units are excluded from binary metrics and included in the survival analysis. Counts are reported.

### Cohort and splits

- The split is chronological by `t0`: train before T1, validation T1 to T2, test T2 to T3.
- A 30-day embargo between splits stops outcome windows from crossing.
- Groups are also split by morphological family (as with `term_family` in G5) and by near-duplicate cluster.
- Never-spread candidates (Y = 0) are kept.

### Baselines

1. **Frequency-only:** log occurrence count, active hours, and active days as of `prediction_ts`.
2. **Morphology-only:** character n-grams, length, formation mechanism hypothesis, and affix and formative indicators.
3. **Morphology+frequency:** 1 and 2 combined. This is the comparison the question names.

### Candidate model

- S2: regularized logistic regression on baseline features plus S1 representation and context features.
- One preregistered configuration, no sweeps on test. Tuning happens on validation only.

### Metrics

- **Primary:** PR-AUC on test, compared with the morphology+frequency baseline, with a grouped bootstrap 95% CI. Bootstrap resample count and seed are fixed at freeze.
- **Secondary:** log loss, ECE, and reliability diagrams.
  - These are backtest metrics and are never written to `brier` fields (spec CR-9).
- **Stratification:** by candidate age at prediction and by frequency bucket.
- **Coverage report:** units total, censored, `NOT_COMPUTABLE`, and excluded for novelty.

### Decision rule

- Success means the lower bound of the PR-AUC difference CI against morphology+frequency is above 0.
- Otherwise the result is negative and is published as is.

### Near-duplicate controls

- Exact copies are matched by `content_sha256` after URL and handle removal (as in `BOTLIKE_REPETITION`).
- Near duplicates use a near-duplicate clustering method and threshold fixed at freeze.
- Copies never count as recurrence. Clusters never span splits.

### Leakage checks

- No feature timestamp is later than `prediction_ts`.
- Guard features are computed as of `prediction_ts`.
- Qualification verdicts are not used as features. They are computed with future data.

## 5. Risks

- **Small attested cohort:** 8 of 9 Oct-13 holds have no rows (F6). The current store may give few novel first occurrences. The power check comes at E2.
- **Author and community coverage:** approved HMAC backfill (2026-10-15) adds them where the source has them; 4chan is mostly anonymous, so independence there is coverage-limited and reported as such.
- **Early signal may be weak.** C2 found innovation-phase prediction weak (AUC about 0.61). Expect a modest effect at Δ = 24 h.
