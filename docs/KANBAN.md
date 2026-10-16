# Hyperlex v2 kanban (steps to data READY)

Updated 2026-10-16 1:05 PM PT (parity pass). Mirrors:
- Notion board: https://app.notion.com/p/f57ad22c76d7436c9e024229be560a8e
- GitHub Project: https://github.com/orgs/Zero-State-LLC/projects/28 (Column field)
- Obsidian: `Projects/Hyperlex v2 board.md`

The Obsidian board is the source of truth. This file carries no slur terms, post text or private rows.

## Readiness: NOT READY
Readiness rule (Danny 2026-10-16 12:45 PT): test-gold coverage (G1) and ruled meanings (T2) are independent checks. Each must be met and verified by its own separate recount; one shared figure never establishes READY.

| Check | Count | Independent recount | Status |
|---|---|---|---|
| G1 test gold (export) | 245/250 | 245 (test.jsonl human S/O = gold_test.jsonl = manifest ids) | SHORT by 5 |
| T2 ruled meanings | 149/300 | 149 (operator_definitions by source: 100 T2 review + 47 queue definitions + 2 chat) | SHORT by 151 |

Ruling landing: 1,439 rulings, 1,396 gold (test 248, val 164, train 984). Export gold: test 245, val 158, train 933. Manifest 245 ids, sha c10826ed…, not frozen.

## Next
- [ ] **Danny decisions on families (private).** Owner: Danny. 1 Kimi low-confidence item and 4 held terms (named in the private store only). 63 rows stay unfamilied until then.
- [ ] **15 quarantined gold rows.** Owner: Danny (decision). Ruled gold rows (3 test, 2 val, 10 train) fail the existing DQ checks (author id present plus suspect synthetic source id). Fix the check, or keep them out.
- [ ] **Reach 300 ruled meanings (T2).** Owner: Grok Bot (drafts), Danny (rulings). 149/300. Plan proposed 2026-10-16: draft meanings for undefined terms with evidence, then collect for undefined terms without posts.

## In progress
- [ ] **Raise test gold to 250 (G1), then 470 (G5).** Owner: Danny (rulings), Grok Bot (queues). Export 245/250 (landing 248); G5 245/470. Test-gap fill: 228 posts collected for 18/21 empty test terms; queues 2026-10-16c (54) and 16d (42) ruled and applied. Queue 2026-10-16e (33 rows, 11 terms) prepared, not sent. tlpur needs context; god shot skipped (insufficient context).
- [ ] **PR #31: T026/T028 (windowed export context, R statuses non-gold, Jev use_mention).** Owner: Danny (merge yes). Opus review findings fixed; 42 tests pass. Not merged.

## Blocked
- [ ] **Freeze the held-out test manifest.** Owner: Grok Bot, with Danny's sign-off. Blocked on G1 reaching 250 and on READY.
- [ ] **Archive repo is read-only (scrimshawlife-ctrl/Hyperlex).** Owner: Danny. Decide: unarchive it, or move VERDICT-RULES into this repo.

## Done
- [x] **Test split supply decision** (Danny 2026-10-16 12:25 PT): collect for the 21 empty test terms; raising the test cap 10→15 only if short. Collected for 18/21 (3 still empty). Top-up not used.
- [x] **Rebuild the training export** (re-run 2026-10-16 12:46 PM PT after queue 16d). Store 9,751 rows; exported 9,446; overlaps 0.
- [x] **Family review: 8 items via Kimi** (moonshotai/kimi-k3). 7 settled; 1 low-confidence item to Danny.
- [x] **Sort the 358 unfamilied rows.** Kimi verdicts plus an Opus sort of new rows (15 terms assigned, 6 to noise, 4 held).
- [x] **T026 export windowing and T028 Jev use_mention** coded with tests (PR #31, unmerged).
- [x] **Betting-sharp replacement pick.** Retired in PR #27 (220c108).
- [x] **Spec 009 Q1-Q5 decisions applied, and the repair queue re-ruled** (2026-10-16).
- [x] **Merge specs 008 and 009 to main.** #28 squash d87e3af, #29 squash 4f17542.
