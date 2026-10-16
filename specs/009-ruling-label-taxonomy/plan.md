# Spec 009 plan: ruling label taxonomy

Status: DRAFT. Mode: SHADOW for everything outside the ruling tool.

## 1. Files

| Location | File | Change |
|---|---|---|
| Operator box (canonical runtime, not in repo) | `hyperlex-v2-tracker/ruling_queue.py` | Implemented: corrections-only mode, multi-part replies, `--update-existing`, auto-reject gate. |
| Repo | `scripts/v2/ruling_queue.py` | Mirror of the tracker copy, for review and CI. Never run against production data. |
| Repo | `tests/test_ruling_queue_v2.py` | 18 tests, passing. |
| Repo | `specs/009-ruling-label-taxonomy/*`, `specs/index.yaml` | This spec and its index entry. |
| Repo | `specs/008-*/spec.md` | Amend CR-5 with a pointer to 009 CR-B. |
| Hyperlex-archive (separate PR, open) | `docs/vernacular/VERDICT-RULES.md`, `contracts/jev_sense_contract.json` | Rule-version bump and the `use_mention` field (blocked on Q3). |
| Operator box (private) | landing file, SQLite store | Ruling rows. No schema migration. |

## 2. CLI: `ruling_queue.py apply`

| Flag | Effect |
|---|---|
| `--answers FILE [FILE...]` | One or more answer files for one queue date. Parts are merged. |
| `--corrections-only` | Forces corrections-only mode. |
| `--no-auto-corrections` | Turns off automatic detection of the "Corrections only" header. |
| `--update-existing` | Upserts in place and records revision fields. Never duplicates rows. |
| `--auto-reject-terms` | Off by default. Writes term rejection only if every landing ruling for the term is R. Not recommended (FR-004). |
| `--write-sqlite` | Also writes the SQLite store. |
| `--dry-run` | Reports new / updated / unchanged / listed / retained counts and writes nothing. |

**Parsing:**
- Accepts several files and "PART n:" comma lists.
- Identical duplicate indices collapse to one entry.
- Conflicting duplicate indices abort the apply before any write.

## 3. Data fields (per ruling row)

| Field | Values | Status |
|---|---|---|
| `answer_mode` | `corrections_only_listed`, `corrections_only_retained`. An absent value on legacy rows means an explicit ruling. | Implemented |
| `revised_from` | Prior label | Implemented |
| `revised_at` | Timestamp (PT) | Implemented |
| `revision_source` | Answer file path | Implemented |
| `ratification_ref` | Answer file and header that ratified retention (DEC-010 provenance) | Open (T018). Until then, `revision_source` carries it. |
| `use_mention` | `USE`, `MENTION` | Open (T015, blocked on Q3) |

## 4. Migration

There is no migration.
- New fields are optional.
- Legacy rows are not rewritten (FR-023).
- The "normie" status row is not touched (FR-005).
- The 2026-10-15 unlisted rows are not backfilled (FR-024).

## 5. Mirror discipline

1. Edit the tracker copy first.
2. Copy it to `scripts/v2/ruling_queue.py` in the same session.
3. Record the tracker file's sha256 in the mirror header.
4. A drift check compares the two hashes on the owner box (T019).

## 6. Tests

`tests/test_ruling_queue_v2.py` currently has 18 tests, all passing. They cover these areas:
- header detection and the corrections-only flags;
- listed vs retained `answer_mode`;
- multi-part and "PART n:" merging;
- abort on conflicting duplicates;
- in-place update with revision fields and idempotent re-runs;
- auto-reject default off, and the all-R requirement.

**Planned additions:**
- the mirror hash check;
- `ratification_ref` on retained rows;
- a test that R rows are never counted as attested (once the 008 builder exists).

**Real-data check (done):** re-running the four 2026-10-16 answer files with `--update-existing --dry-run` gave new 0, updated 0, unchanged 300, listed 91, retained 209.

## 7. Safety

- The fixtures in the mirror and the tests use synthetic terms only.
- No private-list term appears in code, tests, the spec or PR text.
- SC-005 is checked on the owner box against `HYPERLEX_PRIVATE_REGISTRY`.
