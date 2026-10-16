# Spec 009 tasks

## Done

- [x] T001 Detect the "Corrections only" header automatically, and add `--no-auto-corrections` (tracker).
- [x] T002 Add the `--corrections-only` flag.
- [x] T003 Write `answer_mode=corrections_only_listed` / `corrections_only_retained`.
- [x] T004 Support multi-part replies: several files and "PART n:" comma lists for one queue date.
- [x] T005 Abort on conflicting duplicate indices. Collapse identical duplicates.
- [x] T006 `--update-existing`: upsert in place with `revised_from`, `revised_at` and `revision_source`. No duplicate rows.
- [x] T007 Auto-reject off by default, behind `--auto-reject-terms`.
- [x] T008 Auto-reject, when on, requires every landing ruling for the term to be R.
- [x] T009 Add `--dry-run` counts and `--write-sqlite`.
- [x] T010 Add the mirror copy at `scripts/v2/ruling_queue.py`.
- [x] T011 Tests at `tests/test_ruling_queue_v2.py`: 18 passing.
- [x] T012 Apply the 2026-10-16 queue (11:02 AM PT) and training parts 1–3 (11:15 AM PT): S 177, O 90, R 24, U 9.
- [x] T013 Verify idempotence with a dry run: new 0, updated 0, unchanged 300, listed 91, retained 209.

## Open

- [ ] T014 Danny reviews spec 009 and promotes it (constitution VIII).
- [x] T015 Add the `use_mention` field (`USE` / `MENTION`) to `jev_sense_contract` (Hyperlex-archive). Researched: mentions count toward C_ATTESTED only (spec §8 Q3); needs Danny for rule bump.
- [x] T016 Bump VERDICT-RULES (§3 count base, `C_ATTESTED`, `LOW_SENSE_PURITY` treatment of mentions). Researched: mentions count toward C_ATTESTED only (spec §8 Q3); needs Danny for rule bump.
- [x] T017 Audit historical `operator_term_status='rejected'` rows written by auto-reject, starting with "normie". Audited: 8/69 auto-reject rows, all false (spec §8 Q1); supersede on Danny yes.
- [x] T018 Add `ratification_ref` to `corrections_only_retained` rows (DEC-010 provenance).
- [ ] T019 Add a mirror drift check (tracker sha256 vs mirror header).
- [x] T020 Decide on the 2026-10-15 unlisted-row backfill. Researched: 95 rows, reply ratified (spec §8 Q2); apply on Danny go.
- [x] T021 Map forward R to `EXCLUDED_INVALID` or `TARGET_ABSENT`, and amend 008 CR-5 text. Recommend TARGET_ABSENT (spec §8 Q5); needs Danny.
- [x] T022 Confirm the headcanon-class boundary in FR-010. Resolved: S within community (spec §8 Q4); confirm.
- [ ] T023 Make the 008 cohort builder exclude R rows from attestation (SC-007).
- [x] T024 Remove `--auto-reject-terms` if Danny agrees. Recommended remove (spec §8 Q1).
- [ ] T025 Run the SC-005 private-registry check on the owner box before the PR leaves draft.

- [x] T026 Re-window excerpts for the 85 repair rows (50 TARGET_ABSENT + 3 review + 32 flagged), then re-queue (rulings/repair/2026-10-16-target-absent.txt on the operator box).
- [ ] T027 (BLOCKED: remote scrimshawlife-ctrl/Hyperlex is archived/read-only, push 403; v1.5 lives in this spec) Push Hyperlex-archive metrics-rule-v1.5 commit (needs approval; that remote is public).
- [ ] T028 Implement use_mention in the Jev sense labelling runtime.

- T026 done 2026-10-16: queue excerpts are windowed around the target (`window_excerpt`, 500 chars); `ruling_queue.py repair` re-queues landed rows with original_text + previous_label kept. Repair queue 2026-10-16-repair: 85 rows (test 15, val 14, train 56) on the operator box. Re-ruling a TARGET_ABSENT row as non-R moves its status to status_history.
