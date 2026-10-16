# Spec 008: Lexical emergence

- **Status:** DRAFT / SHADOW. Advisory until operator promotion (constitution VIII).
- **Spec id:** 008. `specs/index.yaml` shows 008 as the next free id (F9). The index entry is not part of this file set.
- **Source brief:** Danny, 2026-10-15 21:11 PT. Steering at 21:13 PT: "Conflicts should be researched for proper integration."
- **Intent:** `intent/2026-10-15-lexical-emergence.md`, status draft (awaiting Danny).
- **Depends on:** `.specify/memory/constitution.md` v1.0.0 and spec 007. 007 defines the SHADOW ModernBERT-base trunk.
- **Runtime truth:** This spec changes nothing in `SKILL.md`, `DESIGN.md`, `SPEC.md`, `docs/api-v1.md`, or API_V1.

## 1. Doctrine change (verbatim from brief)

**FROM:** "A single-use expression lacks sufficient adoption evidence and should be rejected."

**TO:** "Every valid lexical innovation is eligible for observation from its first attested occurrence. Adoption, semantic stability, and persistence are future outcomes to measure. Lexical qualification and downstream promotion remain separate decisions."

Corollaries from the brief:

- Repetition is an outcome to measure. It is not a prerequisite.
- R and HOLD mean "not yet established". They do not mean discard.
- Dormancy is not deletion.
- Research eligibility is not production qualification.

The FROM wording does not appear on Hyperlex main (F1). It summarizes the effect of the archived vernacular guards in `Hyperlex-archive: docs/vernacular/VERDICT-RULES.md` v1.4 (commit d43a44a, PR #124).

## 2. Problem

The current vernacular doctrine (VERDICT-RULES v1.4) has two effects on single-use and early expressions:

- Guard flags such as `SINGLE_BURST` and `DORMANT_OR_UNDATED` cap them at OBSERVE or HOLD.
- Ruling code `R` writes status `rejected` (`hyperlex-v2-tracker/ruling_queue.py`, F4).

Training export also deduplicates rows on `content_sha256` (`vi-data/hyperlex_tracker/export_splits.py`, F5).

Together these make the first occurrences of new words invisible to later measurement. Hyperlex is meant to "catch language while it is still becoming culture" (constitution I). It cannot learn which innovations spread unless it keeps every innovation from its first attestation, including the ones that never spread.

The guards still do a needed job: they stop bursts, bot copies, and single-author artifacts from being promoted. This spec keeps that job and stops the guards from deleting observations.

## 3. Key principle: eligibility vs qualification

| Layer | Question | Threshold | Guards | Output |
|---|---|---|---|---|
| **Observation eligibility** | Is this a valid, attested occurrence of a lexical innovation? | None. Hapax legomena are kept. | Not applied as filters. Computed as measured features and outcome labels. | Immutable OccurrenceRecord. Candidate registered with a stable id. |
| **Qualification** | Does the term meet production evidence rules? | VERDICT-RULES v1.4 paths A–D, unchanged. | All 8 guard flags, unchanged. They still block PASS. | PASS / OBSERVE / QUARANTINE / HOLD, unchanged. |
| **Promotion** | Should anything downstream act on it? | Operator gate (VIII). Abraxas arbitration. | n/a | Always `SHADOW_ONLY` from Hyperlex. |

## 4. User stories

- **US1 (operator):** A word seen once today is still in the registry next month. I can see whether it came back, spread, or went dormant. Nothing was silently dropped.
- **US2 (researcher):** I want time-separated cohorts that include never-spread words. Then I can test whether Hyperlex beats frequency and morphology baselines at predicting recurrence.
- **US3 (operator):** Existing PASS/OBSERVE/QUARANTINE/HOLD verdicts must not change because of this spec. Guard flags must still block PASS.
- **US4 (Abraxas consumer):** I receive a versioned EmergenceEvidence payload. It never claims a hypothesis is verified and never promotes.
- **US5 (safety reviewer):** No slur-list term, post text, or raw author handle appears in this repo or in public artifacts.

## 5. Functional requirements

**Observation (E0)**

- **FR-001** Ingestion MUST preserve every valid attested occurrence, including hapax legomena. No minimum count, author count, day count, or recency applies to storage.
- **FR-002** Each occurrence MUST be stored as an immutable OccurrenceRecord (`contracts/occurrence_record.v1.schema.json`) with these fields:
  - observed timestamp (`event_time`) and ingested timestamp (`collected_at`)
  - source ids, provenance, language, community, span, and source and content hashes
  - rights, recorded as provenance only
  - extraction quality
  - privacy-safe author pseudonym
- **FR-003** Corrections MUST create a new record that names the old one in `supersedes`. Historical record hashes and `provenance.integrity` MUST NOT be rewritten (constitution VI).
- **FR-004** A `DISCOVERY_HIT` (for example a dictionary hit) MUST NOT count as an attested occurrence. It can register an `UNATTESTED` candidate only.
- **FR-005** Exact and near duplicates MUST be kept and marked (`dedup.exact_duplicate_of`, `dedup.near_dup_cluster_id`). They are excluded from independence counts, not deleted.
- **FR-006** Replay from source MUST reproduce identical `record_hash` values.

**Interpretation (E1)**

- **FR-007** The candidate registry MUST assign stable `candidate_id` values without any qualification.
- **FR-008** Sense hypotheses MUST be provisional by default. Several competing hypotheses MAY coexist. `gloss` MAY be null, so no meaning is forced.
- **FR-009** Morphological similarity MUST NOT imply identity. Related candidates are linked by typed relations. A merge requires an operator-gated merge record (the -slop rule, data-model §6).
- **FR-010** Context meanings are `INFERRED`, operator definitions are `OBSERVED`, and next-form guesses are `SPECULATIVE` (constitution IV, VERDICT-RULES §7).

**Emergence (E2–E4)**

- **FR-011** Temporal features MUST be computed as of a frozen timestamp: frequency, recurrence, acceleration, days since last use, and dormancy.
- **FR-012** Diffusion features MUST be computed when the needed columns exist: independent authors and communities. Otherwise they are `NOT_COMPUTABLE`, with no silent proxy.
- **FR-013** The four guard flags `SINGLE_BURST`, `ONE_AUTHOR_DEPENDENCE`, `BOTLIKE_REPETITION`, and `DORMANT_OR_UNDATED` MUST also be computed as measured features in EmergenceEvidence. They use only as-of data, at the VERDICT-RULES v1.4 thresholds.
- **FR-014** Forecasts MUST be written as ForecastReceipts with these fields:
  - frozen `prediction_ts`
  - window, target, and horizon
  - feature snapshot hash
  - censoring status
  - a later outcome block
- **FR-015** Right-censoring is mandatory. Windows that pass the data end or a coverage gap are censored, not labelled negative.
- **FR-016** Forecast targets are experimental:

  | Target | Horizons |
  |---|---|
  | Recurrence | 7 or 30 days |
  | Adoption (distinct author) | 7, 30, or 90 days |
  | Diffusion (another community) | 7, 30, or 90 days |
  | Persistence | 30 or 90 days |
  | Semantic stability | 7, 30, or 90 days |
  | Mutation | 7, 30, or 90 days |

- **FR-017** Evaluation MUST use the following:
  - time-separated cohorts that include never-spread candidates
  - chronological splits and frozen feature snapshots
  - duplicate and near-duplicate controls, and coverage reports
  - PR-AUC and calibration, stratified by age and frequency
  - frequency-only, morphology-only, and morphology+frequency baselines

**Qualification and promotion**

- **FR-018** VERDICT-RULES v1.4 thresholds, paths, and guards MUST stay unchanged and MUST still gate PASS. Any threshold change requires a rule-version bump (VERDICT-RULES §8).
- **FR-019** Qualification output MUST be stored beside, not instead of, observation state (`qualification` block in CandidateHypothesis).
- **FR-020** EmergenceEvidence MUST carry `verified: false` and `promotion: "SHADOW_ONLY"`. Hyperlex never declares a hypothesis verified.
- **FR-021** Any `brier` field MUST be null unless all of these hold:
  - the forecast class is operator-approved as eligible
  - an operator settlement has decided TRUE or FALSE

  Backtest calibration MUST NOT be written into `brier` fields (constitution III).
- **FR-022** Hyperlex MUST NOT import Abraxas. The E5 payload is export-only under `hyperlex.compat.abraxas` (constitution V).

**Safety and privacy**

- **FR-023** For private-overlay members (`HYPERLEX_PRIVATE_REGISTRY`, F7):
  - `surface` MUST be null in records.
  - `candidate_id` MUST be opaque.
  - Content and safety metadata MUST reference the overlay, not text.
- **FR-024** No post text in repo artifacts. Context is referenced by `context_ref` into the private store.
- **FR-025** Author identity is stored only as a keyed pseudonym. The key stays in the private store. Raw handles are never stored.
- **FR-026** When `restricted_intent_suspected` is true, store only hash and layer tags (constitution VII).
- **FR-027** Rights are provenance only, never an eligibility filter (F7, PR #26).

**Packaging**

- **FR-028** New code ships as a library module under `hyperlex.analysis.*` with tests before any CLI (constitution IX). The module name is decided at the implement stage. Additive symbols go on `API_EXTENDED`.
- **FR-029** Schemas in `contracts/` are draft contracts. Landing them in `schemas/` is an operator gate.

## 6. Three dimensions

| Dimension | Question | Stored in | Claim label |
|---|---|---|---|
| Observation | Was it used? When, where, and by whom (pseudonym)? | OccurrenceRecord (immutable) | OBSERVED for attested surface |
| Interpretation | What might it mean? Which hypotheses compete? | CandidateHypothesis `sense_hypotheses`, `formation` | INFERRED / SPECULATIVE |
| Emergence | Does it spread, stabilize, mutate, or disappear? | EmergenceEvidence, ForecastReceipt | Measures OBSERVED or NOT_COMPUTABLE; forecasts SPECULATIVE |

## 7. Lifecycle

- **`lexical_status`:**
  - `UNATTESTED`: discovery hit only, 0 occurrences.
  - `OBSERVED`: at least 1 attested occurrence.
  - `EXCLUDED_INVALID`: not a valid lexical innovation, for example a tokenization error or a proper name. The record is kept and excluded from cohorts. It is reversible by revision.
- **`emergence.trajectory`:**
  - `INSUFFICIENT_HISTORY` leads to `RECURRING`, `SPREADING`, `STABILIZING`, `MUTATING`, or `DORMANT`.
  - `DORMANT` leads to `REVIVED`.
- **Dormancy:**
  - A candidate is `DORMANT` when no attested occurrence falls inside the dormancy window over covered time. The default window is 60 days, matching `DORMANT_OR_UNDATED`.
  - Dormant candidates are never deleted. They keep their occurrences and stay eligible for revival.
  - Open forecasts on a dormant candidate resolve normally, or are censored when coverage is missing.
- **Qualification:** runs independently at its own rule version. HOLD and QUARANTINE stay final for the verdict and are never upgraded. They do not stop observation.

## 8. Boundaries

| System | Owns | Does not own |
|---|---|---|
| Hyperlex | candidates, morphology, representation (SHADOW ModernBERT-base trunk, spec 007), occurrence tracking, emergence measurement, forecasts as SPECULATIVE receipts | verification, promotion, Abraxas registry rows, p89 binds, Forecast spines |
| Noesis | stability and invariants checks over emergence evidence | raw occurrence capture |
| Trutina | calibration against settled outcomes | creating settlements |
| Abraxas | arbitration, governance, promotion, independent verification | Hyperlex internals. Hyperlex never imports it. |

Interfaces to Noesis and Trutina are not defined on Hyperlex main. They are UNVERIFIED and limited to the payloads in `contracts/`.

## 9. Non-goals

- No revival of the rejected "V6 classifier". F2 found no definition on main. This spec builds no classifier that issues authoritative accept or reject labels on terms.
- No change to VERDICT-RULES v1.4 thresholds, the Jev contracts, or `ruling_queue.py` in this PR.
- No live ingest, cron, settlement, hub publish, or spend. These are owner-gated.
- No numeric Brier on open forecasts.
- No generation of restricted wraps or payloads.
- No merging of morphologically similar terms.
- No implementation code in this PR. Docs only.

## 10. Constitution check (I–X)

| # | Principle | Result |
|---|---|---|
| I | Becoming-culture | PASS. First occurrences are preserved, and lineage and mutation relations are typed. |
| II | Offline-first, fail closed on scores | PASS. All features are as-of from the local store. Missing columns produce `NOT_COMPUTABLE`. |
| III | Settled Brier only | PASS. Brier is schema-enforced null unless an eligible class has an operator TRUE/FALSE settlement. Backtests use PR-AUC, log loss, and reliability. |
| IV | Provenance labels | PASS. Every record and hypothesis carries OBSERVED, INFERRED, or SPECULATIVE. |
| V | No Abraxas import | PASS. The E5 payload is export-only. |
| VI | Frozen receipts | PASS. Occurrences are immutable and corrections supersede. Forecast prediction fields are write-once. |
| VII | Detector over generator | PASS. Restricted-intent records store hash and tags only. |
| VIII | Human promotion | PASS. `SHADOW_ONLY` is a const. Schema landing, the index entry, and merges are operator-gated. |
| IX | Library-first | PASS (planned). Code goes in a `hyperlex.analysis.*` module with tests first. API_V1 is untouched. |
| X | Dual-use bound | PASS. No slur names, no post text, and private overlay references only. |

## 11. Oct-13 holds

The brief says to move these to the emergence registry **if the occurrences are genuine**. F6 checked them against the private store:

| Term | Rows in store | Genuineness | Proposed registry state |
|---|---|---|---|
| goreslop | 10 (disposition OBSERVED) | Rows present. Pending the E0 replay check. Content and safety metadata go via the private overlay reference only. | `OBSERVED` after replay passes |
| technoslop | 0 | UNVERIFIED | `UNATTESTED` |
| protslop | 0 | UNVERIFIED | `UNATTESTED` |
| canon-event | 0 | UNVERIFIED | `UNATTESTED` |
| swamp-dog | 0 | UNVERIFIED | `UNATTESTED` |
| ripofflican | 0 | UNVERIFIED. Found via vernacular-discovery-v1 from Wiktionary only. first_seen = last_seen = 2026-10-11 13:42 PT. "No observations". | `UNATTESTED` |
| lowkenuinely | 0 | UNVERIFIED | `UNATTESTED` |
| piddlefart | 0 | UNVERIFIED | `UNATTESTED` |
| throat-sweats | 0 | UNVERIFIED | `UNATTESTED` |

- Genuineness is UNVERIFIED for 8 of 9.
- Dictionary discovery hits are not attested occurrences (FR-004).
- `UNATTESTED` candidates have no first-attestation timestamp. They enter no cohort until an attested occurrence is ingested.
- technoslop, protslop, and goreslop are separate candidates (FR-009).

## 12. Success criteria

- **SC-001** E0 replay reproduces 100% of valid occurrences with identical `record_hash`. Zero occurrences are dropped by count, recency, or dedup.
- **SC-002** Recomputing VERDICT-RULES v1.4 verdicts for all existing terms gives the same verdicts and guard flags as before this spec.
- **SC-003** All four contract schemas validate as JSON Schema 2020-12. Fixtures with non-null `brier` on unsettled receipts fail validation.
- **SC-004** Every forecast receipt has a frozen `prediction_ts` earlier than its outcome window. Censored windows never carry an `outcome_value`.
- **SC-005** The first experiment (plan §4) is preregistered and hashed before test data is loaded. Results are reported either way, including negative results.
- **SC-006** A scan of the repo diff finds no post text, raw handles, or slur-list terms.

## 13. Conflict reconciliation

Each entry gives the existing rule and why it exists, the research basis, the integration, and the residual risk. Guard thresholds below are quoted from `Hyperlex-archive: docs/vernacular/VERDICT-RULES.md` v1.4 §5 (commit d43a44a, PR #124).

### CR-1 `SINGLE_BURST`

- **Existing rule:** The flag is raised when a term has fewer than 2 active days, or 80% or more of its posts fall on one day. It blocks PASS.
  - Why it exists: to stop promotion of bursts that are not sustained use (F1).
  - Receipts show it in use, for example 'smol bean (OBSERVE) flags SINGLE_BURST' and 'anchovy (HOLD) … SINGLE_BURST'.
- **Research basis:**
  - C2 separates 251 "buzzes" from 141 lasting "changes" among 392 innovations. Bursts are a main class of fate, so they must be kept as data.
  - C1 reports high volatility (coefficient of variation) in neologism time series.
  - C3 applied a minimum-frequency threshold of 10 as an analysis choice, not a storage rule.
- **Integration:**
  - Storage applies no burst filter.
  - `SINGLE_BURST` is computed as an as-of feature (FR-013) and used as an outcome label, "burst then dormant".
  - The qualification guard is unchanged and still blocks PASS.
- **Residual risk:**
  - Computing the flag with post-prediction data would leak the outcome. Mitigation: as-of computation and frozen snapshots.
  - Burst-heavy cohorts may dominate negatives. Mitigation: stratify by frequency.

### CR-2 `ONE_AUTHOR_DEPENDENCE`

- **Existing rule:** The flag is raised when one author wrote more than half of the slang-sense posts. It blocks PASS.
  - Why it exists: to stop single-author artifacts (F1).
- **Research basis:**
  - C2: adopter and network position decide fate during propagation (precision about 0.81, AUC about 0.86). Early adopter profiles alone are weak (precision about 0.56, AUC about 0.61).
  - C3: network structure modulates the rate of lexical change.
  - So author structure is the signal to measure.
- **Integration:**
  - The flag becomes a measured feature.
  - "Adoption by a distinct author" is a forecast target. It is the measured way a term leaves single-author status.
  - The guard still blocks PASS.
  - The flag is `NOT_COMPUTABLE` until author pseudonyms exist (CR-7).
- **Residual risk:**
  - Sockpuppets defeat pseudonymous distinctness.
  - Until author columns exist, adoption targets cannot be evaluated.

### CR-3 `BOTLIKE_REPETITION`

- **Existing rule:** The flag is raised when half or more of the posts are identical copies after removing URLs and handles. It blocks PASS.
  - Why it exists: to stop bot copies from counting as adoption (F1).
- **Research basis:**
  - C3 counted usage with a frequency threshold, so analysis counts depend on what is counted.
  - Independent recurrence needs copy control.
- **Integration:**
  - Copies are kept and marked with `exact_duplicate_of` and `near_dup_cluster_id`.
  - Copies are excluded from independence counts and recurrence outcomes.
  - Bot fraction is a feature.
  - The guard is unchanged.
- **Residual risk:**
  - Paraphrasing bots evade near-duplicate detection.
  - The near-duplicate method and its threshold must be preregistered.

### CR-4 `DORMANT_OR_UNDATED`

- **Existing rule:** The flag is raised when there is no use in the last 60 days, measured against the newest post in the database, or when there is no dated post. It blocks PASS.
  - Why it exists: so stale or undated terms are not promoted.
- **Research basis:**
  - C1 reports high volatility. Neologisms fall away and return.
  - C2 treats fate as an outcome over time.
- **Integration:**
  - `DORMANT` is a lifecycle state. It never deletes, and revival is measurable.
  - For emergence, dormancy is computed over covered time, so ingest gaps are censored rather than counted as silence.
  - Undated occurrences (`observed_at` null) are kept and excluded from temporal cohorts.
  - The qualification guard is unchanged, including its "newest post in database" reference.
- **Residual risk:**
  - The two dormancy definitions (guard vs coverage-aware) can disagree.
  - Both are stored and labelled. Neither is silently substituted.

### CR-5 Ruling code `R` (REJECT) and HOLD

- **Existing rule:**
  - `ruling_queue.py` codes are S, O, U, and R. R writes status `rejected` (F4). Rulings from 2026-10-13 include R.
  - VERDICT-RULES §2: HOLD and QUARANTINE are final and never upgraded.
  - G5 preregistration (`docs/v2/G5_PREREG_EVAL.md`) excludes UNSURE and REJECT rows.
  - Why these exist: to keep bad rows out of gold and training.
- **Research basis:**
  - C2's never-spread innovations are needed as negatives. Discarding them biases the cohort toward survivors.
  - This is a design inference from C2, not a claim the paper makes.
- **Integration:**
  - Rulings are copied unchanged into `legacy.ruling_code` and `legacy.human_ruling`. No code or historic row changes.
  - R and HOLD are read as qualification judgments, "not yet established". The occurrence stays.
  - If a ruling means the record is unusable (not a lexical innovation), the candidate becomes `EXCLUDED_INVALID`. It is kept and excluded from cohorts.
  - HOLD stays final for the verdict, and observation continues.
  - G5 exclusions are unchanged.
- **Residual risk:** Historical R rulings may mix "invalid" and "not established". See open question Q3.

### CR-6 Text-hash dedup

- **Existing rule:** `vi-data/hyperlex_tracker/export_splits.py` dedupes train, val, and test on `content_sha256` (F5).
  - Why it exists: to prevent train/test leakage. This is correct for training.
- **Research basis:** Leakage control is required. The observation store has a different job, which is completeness.
- **Integration:**
  - Dedup stays in export only.
  - The observation store keeps all records. The earliest `observed_at` in a hash group is the canonical first occurrence, and later ones are marked duplicates.
  - Evaluation groups splits by near-duplicate cluster and by candidate, so the same text never spans splits.
- **Residual risk:** If export dedup keeps a later copy rather than the earliest, first-occurrence timestamps differ between export and store. Task T018 checks this.

### CR-7 Missing author and community columns

- **Existing rule:** `slang_v1.sqlite3` has no author id and no community column (F3).
  - Why: the store was built from vernacular-ingest for sense work, not diffusion.
- **Research basis:** C1, C2, and C3 all depend on user and network or community structure. Without it, diffusion cannot be measured.
- **Integration:**
  - Schema fields `author_pseudonym` and `community_id` are nullable.
  - Diffusion, adoption, and `ONE_AUTHOR_DEPENDENCE` features are `NOT_COMPUTABLE` with a coverage fraction.
  - No silent proxy. `source_system` is not a community.
  - Adding pseudonyms needs re-ingest from the source, which is owner-gated live ingest (Q2).
- **Residual risk:**
  - The first experiment's "independent" recurrence depends on author pseudonyms. Without them, it reports `NOT_COMPUTABLE` (plan §4).
  - A keyed pseudonym is still linkable inside the private store.

### CR-8 `SHADOW_INSTRUMENT_ONLY`, the V6 classifier, and the instrument interface

- **Existing rule:**
  - Neither term is defined on Hyperlex main. Both are defined in sibling repo argotide `docs/EVIDENCE.md` (fetch-spec refresh 2026-10-02, OBSERVED documentary evidence): "S1 and the Instrument V1 settlement now report V6 final-label classifier REJECTED, with Instrument V1 a separate SHADOW_INSTRUMENT_ONLY measurement layer."
  - No instrument-interface schema exists on main. The nearest are `schemas/*.v1` and the export-only `hyperlex.compat.abraxas` shapes (F2).
  - Why: the V6 final-label classifier was rejected; the measurement layer was kept, but only as a shadow instrument that labels nothing authoritatively.
- **Research basis:** argotide `docs/EVIDENCE.md` line 49 (internal source).
- **Integration:**
  - 008 adopts the argotide meaning: Hyperlex emergence outputs are Instrument-V1-style measurements, never final labels, never gate anything, never `verified`, always `promotion: SHADOW_ONLY`. Encoded as consts in `emergence_evidence.v1`.
  - S1–S4 models produce measurements and forecasts with frozen receipts, not final labels. No component in 008 emits a final lexical label, so the V6 final-label classifier is not revived (non-goal check: any task that outputs an authoritative label fails review).
  - EmergenceEvidence v1 is the proposed payload contract; transport is an export-only compat shape at E5.
- **Residual risk:** The Instrument V1 settlement text itself is not in this repo; a future task should vendor or link it so the definition is checkable from main.

### CR-9 Settled Brier vs forecasts

- **Existing rule:**
  - Constitution III: numeric Brier exists only after operator settlement on an eligible class.
  - `forecast.v1` never carries Brier, and its `signal_key` enum is fixed.
  - `settlement.v1` defines TRUE, FALSE, VOID, and CONFLICT.
  - Why: no self-scoring of open predictions.
- **Research basis:**
  - C2 reports precision and AUC for fate prediction, so discrimination metrics are standard.
  - Brier is not required for research evaluation.
- **Integration:**
  - ForecastReceipt is a separate 008 contract. `forecast.v1` is not edited and its enum is not extended (API frozen).
  - `brier` is schema-forced null unless all of these hold:
    - `forecast_class_eligible` is true, which is an operator decision
    - settlement is SETTLED with TRUE or FALSE
    - authority is `operator`
  - Backtests report PR-AUC, log loss, ECE, and reliability diagrams in eval reports, never in `brier` fields.
  - Trutina calibrates only against settled outcomes.
- **Residual risk:** Readers may treat backtest calibration as settled skill. Mitigation: reports label it backtest and SPECULATIVE.

### CR-10 No Abraxas import vs E5 integration

- **Existing rule:** Constitution V says Hyperlex must not import Abraxas or write its registry rows, p89 binds, or Forecast spines. Compat shapes are export-only.
- **Research basis:** n/a. This is an architecture rule.
- **Integration:**
  - E5 publishes EmergenceEvidence through an export-only compat shape. Abraxas reads it.
  - Independent verification and promotion happen on the Abraxas side.
  - Hyperlex payloads always carry `verified: false`.
- **Residual risk:** A consumer may misread evidence as verification. Mitigation: const fields, and Abraxas-side gating outside this repo.

### CR-11 Slurs and the private overlay

- **Existing rule:**
  - PR #27 (220c108): sensitive members load from the uncommitted `HYPERLEX_PRIVATE_REGISTRY`.
  - Slur-ruled terms live only in the private slur list (F7).
  - Constitution VII and X apply.
- **Research basis:** n/a. This is a safety rule.
- **Integration:**
  - Overlay members may be observed in the private store only, as research eligibility.
  - In records, `surface` is null and `surface_sha256` is keyed.
  - `candidate_id` is opaque, of the form `lex-h-<keyed hash>`.
  - `safety.private_overlay_ref` points into the overlay.
  - goreslop content and safety metadata use the overlay reference only.
  - Nothing in the repo names a slur-list term.
- **Residual risk:**
  - An unkeyed hash of a short word can be brute-forced, so keyed hashing is required.
  - Key custody is owner-side (Q2).

### CR-12 Rights

- **Existing rule:** PR #26 (170e97e): rights are provenance only, not a filter (F7). The brief agrees.
- **Research basis:** n/a.
- **Integration:**
  - `rights` is carried on every OccurrenceRecord and never affects eligibility.
  - Publication of any content stays owner-gated. No post text is in the repo anyway.
- **Residual risk:** Rights-restricted content sits in the private store. Legal review is owner-gated and is not decided here.

## 14. Open questions for Danny

Research cannot settle these.

- **Q2:** Do you approve re-ingest from vernacular-ingest to add keyed author pseudonyms and a community field? This is owner-gated live ingest. Who holds the key?
- **Q3:** For the 2026-10-13 `R` rulings, did R mean "invalid or unusable record" (maps to `EXCLUDED_INVALID`) or "not yet established" (stays `OBSERVED`)? Or should those rows be re-ruled?
- **Q5:** For the 8 Oct-13 holds with 0 rows, is there a source where you saw attested uses? If not, they stay `UNATTESTED`.
- **Q6:** What should count as a "community" for diffusion in Hyperlex sources? This is a product choice once the column exists.

## 15. References

- **C1 (VERIFIED):** "Social Networks of Lexical Innovation. Investigating the Social Dynamics of Diffusion of Neologisms on Twitter". Frontiers in Artificial Intelligence, 2021. doi:10.3389/frai.2021.648583. https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2021.648583/full. Authors UNVERIFIED.
- **C2 (VERIFIED):** "How position in the network determines the fate of lexical innovations on Twitter". PLOS Complex Systems, 2024. doi:10.1371/journal.pcsy.0000005. https://journals.plos.org/complexsystems/article?id=10.1371%2Fjournal.pcsy.0000005. Authors UNVERIFIED.
- **C2 companion:** Tarrade, Magué, Chevrot 2022. doi:10.2478/plc-2022-15. https://doi.org/10.2478/plc-2022-15 (VERIFIED by lookup).
- **C3 (VERIFIED):** Zhu and Jurgens, "The structure of online social networks modulates the rate of lexical change", NAACL 2021. https://aclanthology.org/2021.naacl-main.178.
- **JSON Schema 2020-12:** https://json-schema.org/draft/2020-12/schema (meta-schema used by repo `schemas/`).
- **Internal sources (not URLs):**
  - `Hyperlex-archive: docs/vernacular/VERDICT-RULES.md` v1.4 (d43a44a, PR #124)
  - `hyperlex-v2-tracker/ruling_queue.py`
  - `vi-data/hyperlex_tracker/export_splits.py`
  - private store `slang_v1.sqlite3`
  - argotide `docs/EVIDENCE.md`
  - `docs/shadow-hyperlexical.md`
  - `docs/v2/G5_PREREG_EVAL.md`
  - `.specify/memory/constitution.md`
