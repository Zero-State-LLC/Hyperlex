# Data model 008: Lexical emergence

Status: DRAFT / SHADOW. Contracts are in `contracts/`. All records live in the private store. Nothing here holds post text or raw author handles.

## 1. Entities

| Entity | Mutability | Contract | Purpose |
|---|---|---|---|
| OccurrenceRecord | **Immutable.** Corrections are new records with `supersedes`. | `occurrence_record.v1` | One attested use, mention, or discovery hit |
| CandidateHypothesis | **Revisable.** Append-only revisions with `revision` and `revised_at`. | `candidate_hypothesis.v1` | Stable candidate, provisional senses, formation, status, legacy qualification |
| SenseHypothesis | Inside a candidate revision | (part of candidate) | Competing provisional meanings; gloss may be null |
| EmergenceEvidence | Immutable per `as_of` | `emergence_evidence.v1` | SHADOW measurement payload: never verified, never promotes |
| ForecastReceipt | Prediction fields write-once. The outcome block is filled once. Any change is a new receipt with `supersedes`. | `forecast_receipt.v1` | Frozen forecast, censoring, outcome, optional settlement |
| QualificationRecord | Produced by VERDICT-RULES v1.4, unchanged | stored in `candidate.qualification` | PASS / OBSERVE / QUARANTINE / HOLD and guard flags |
| MergeRecord | Operator-gated only | future | The only way two candidates become one |

## 2. Key fields

- **OccurrenceRecord:**
  - Ids and links: `occurrence_id`, `candidate_id`, `context_ref` (pointer, no text).
  - Surface: `surface` (null for overlay members), `surface_sha256`.
  - Kind and quality: `occurrence_kind` (`ATTESTED_USE`, `ATTESTED_MENTION`, `DISCOVERY_HIT`), `genuineness`, `extraction_quality`.
  - Time: `observed_at` (null means undated), `ingested_at`.
  - Source and hashes: `source{...}`, `content_sha256`, `record_hash`.
  - Location and context: `span`, `language`, `community_id`.
  - Identity and rights: `author_pseudonym` (keyed hash), `rights` (provenance only).
  - Labels: `provenance_label`, `dedup{exact_duplicate_of, near_dup_cluster_id}`, `safety{sensitivity, private_overlay_ref, restricted_intent_suspected}`.
  - History: `legacy{...}`, `supersedes`.
- **CandidateHypothesis:**
  - Identity: `candidate_id`, `revision`, `surface`, `surface_sha256`.
  - Observation status: `lexical_status`, `occurrence_count` (derived from attested, non-failed occurrences), `first_attested_at`.
  - Interpretation: `sense_hypotheses[]`, `formation{mechanism, components}`.
  - Emergence: `emergence{trajectory, prediction}`, `related_candidates[]`, `merged_into`.
  - Qualification and safety: `qualification{rule_version, verdict, guard_flags}`, `promotion` (const `SHADOW_ONLY`), `safety`.

## 3. Lifecycle states

- **`lexical_status`:**
  - `UNATTESTED`: 0 occurrences.
  - `OBSERVED`: at least 1 occurrence.
  - `EXCLUDED_INVALID`: kept, not in cohorts, reversible by revision.
- **`emergence.trajectory`:**
  - `INSUFFICIENT_HISTORY` is the default at first attestation.
  - It moves to one of `RECURRING`, `SPREADING`, `STABILIZING`, `MUTATING`, or `DORMANT`.
  - `DORMANT` moves to `REVIVED` on a new attested occurrence.
- **Sense `status`:** `PROVISIONAL`, `COMPETING`, `CONTEXT_SUPPORTED` (INFERRED), `OPERATOR_DEFINED` (OBSERVED), `UNRESOLVED`, `WITHDRAWN`.
- Nothing is deleted on dormancy, HOLD, R, or QUARANTINE.

## 4. Mapping from existing store columns (F3)

Source: private `slang_v1.sqlite3`, tables `validated_sense_observation`, `curated_sense_observation`, `quarantine_sense_observation`, and `gold_eval`.

| Store column | 008 field | Note |
|---|---|---|
| record_id | `legacy.record_id`; seeds `occurrence_id` | |
| schema_version | `legacy.schema_version` | |
| source_system, source_table, source_row_key, source_db_sha256 | `source.*` | |
| provenance | `provenance_label` (if OBSERVED, INFERRED, or SPECULATIVE) | |
| event_time | `observed_at` | observed time |
| collected_at | `ingested_at` | ingest time |
| rights | `rights` | provenance only |
| sensitivity | `safety.sensitivity` | |
| review_status | `legacy.review_status` | |
| evidence_link | `source.source_locator` | |
| term | `surface` (null if overlay member) and `surface_sha256` | |
| term_family | split grouping only; **not identity** | |
| contextual_use | **not copied.** Referenced by `context_ref`. | no text in contracts |
| content_sha256 | `content_sha256`, plus dedup | |
| sense_candidate | `sense_hypotheses[].gloss` (status PROVISIONAL) | |
| mutation_lineage | `related_candidates[]` (COMPOUND_PARENT / MUTATION_OF) | INFERRED |
| model_proposal | `sense_hypotheses[]` (SPECULATIVE) | |
| independent_evidence | input to `genuineness` | |
| human_ruling | `legacy.human_ruling`, `legacy.ruling_code` (S/O/U/R) | R is not deletion (spec CR-5) |
| rule_version (slang.disposition.v1), disposition | `legacy.rule_version`, `legacy.disposition` | 285 REJECTED rows are kept |
| epistemic_basis | `legacy.epistemic_basis` | |
| candidate_status (all NULL) | superseded by `lexical_status` | |
| *(none)* | `author_pseudonym` | **missing.** NOT_COMPUTABLE until re-ingest |
| *(none)* | `community_id` | **missing.** NOT_COMPUTABLE |

## 5. Example: ripofflican

**Illustrative (brief).** These values are not a real record:

```json
{
  "candidate_id": "lex-ripofflican",
  "surface": "ripofflican",
  "occurrence_count": 1,
  "lexical_status": "OBSERVED",
  "sense_hypotheses": [{"gloss": "Republican accused of profiting from political power", "status": "PROVISIONAL", "confidence": null}],
  "formation": {"mechanism": "blend", "components": ["ripoff", "Republican"]},
  "emergence": {"trajectory": "INSUFFICIENT_HISTORY", "prediction": null},
  "promotion": "SHADOW_ONLY"
}
```

The brief's single `sense_hypothesis` object becomes one element of `sense_hypotheses[]`.

**Actual state per F6:**

- 0 rows in the store.
- Discovered from Wiktionary only via vernacular-discovery-v1. first_seen = last_seen = 2026-10-11 13:42 PT.
- Resulting values:
  - `lexical_status: UNATTESTED`
  - `occurrence_count: 0`
  - `first_attested_at: null`
  - one OccurrenceRecord of kind `DISCOVERY_HIT` with `genuineness: UNVERIFIED`
  - qualification `NOT_EVALUATED`
- It enters no cohort until an attested occurrence exists.

## 6. -slop non-identity rule

technoslop, protslop, and goreslop share the formative "-slop". The rule:

- Each is a separate `candidate_id` with its own occurrences, counts, and forecasts.
- They are linked only by `related_candidates[].relation = SHARES_FORMATIVE` (INFERRED).
- No relation type implies identity. Counts never pool across related candidates.
- Family-level aggregates are separate derived views and are labelled as such.
- Two candidates become one only by an operator-gated MergeRecord, which sets `merged_into`. History is kept.
- goreslop content and safety metadata go via `safety.private_overlay_ref` only.

## 7. Privacy and safety

- `author_pseudonym` is a keyed hash. The key is in the private store and owner-held.
- Overlay members have `surface: null`, an opaque `candidate_id` (`lex-h-…`), and a keyed `surface_sha256`.
- `restricted_intent_suspected: true` means hash and tags only.
