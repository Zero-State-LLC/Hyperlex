# Hyperlex v2 kanban (steps to data READY)

Updated 2026-10-16 1:15 PM PT (queue 2026-10-16e applied). Mirrors:
- Notion board: https://app.notion.com/p/f57ad22c76d7436c9e024229be560a8e
- GitHub Project: https://github.com/orgs/Zero-State-LLC/projects/28 (Column field)
- Obsidian: `Projects/Hyperlex v2 board.md`

The Obsidian board is the source of truth. This file carries no slur terms, post text or private rows.

## Readiness: NOT READY
Readiness rule (Danny 2026-10-16 12:45 PT): test-gold coverage (G1) and ruled meanings (T2) are independent checks. Each must be met and verified by its own separate recount; one shared figure never establishes READY.

| Check | Count | Independent recount | Status |
|---|---|---|---|
| G1 test gold rows (export) | 274/250 | 274 (test.jsonl human S/O = gold_test.jsonl = manifest ids) | MET (rows) |
| G1 term breadth (roadmap >=150 terms) | 37 terms | 37 | NOT MET; Danny to confirm the clause applies |
| T2 ruled meanings | 318/300 | (A) 318 definitions; (B) 150 pre-16m + 168 from the 16m and disc ruling ledgers = 318 (Danny 2026-10-16 3:29 and 3:52 PM PT). 171 with >=3 store contexts / 157 with >=3 slang contexts | MET |

Ruling landing: 1,472 rulings, 1,425 gold (test 277, val 164, train 984). Export gold: test 274, val 158, train 933. Manifest 274 ids, sha 57543bbd…, not frozen.

## Next
- [ ] **Danny decisions on families (private).** Owner: Danny. 1 Kimi low-confidence item and 4 held terms (named in the private store only). 63 rows stay unfamilied until then.
- [ ] **15 quarantined gold rows.** Owner: Danny (decision). Ruled gold rows (3 test, 2 val, 10 train) fail the existing DQ checks (author id present plus suspect synthetic source id). Fix the check, or keep them out.
- [x] **Reach 300 ruled meanings (T2).** Owner: Grok Bot (drafts), Danny (rulings). 318/300 MET 2026-10-16 4:05 PM PT after queues 16m and disc (65 new term rows; export byte-identical, 0 split changes).

## In progress
- [ ] **Raise test gold to 250 (G1), then 470 (G5).** Owner: Danny (rulings), Grok Bot (queues). Rows: export 274/250 met (recount 274; landing 277); G5 274/470; 37 test terms (roadmap >=150 open). Test-gap fill: 228 posts for 18/21 empty test terms; queues 2026-10-16c (54), 16d (42), 16e (33) ruled and applied. tlpur needs context.
- [x] **PR #31: T026/T028 (windowed export context, R statuses non-gold, Jev use_mention).** Danny merge yes 2026-10-16 4:28 PM PT.

## Blocked
- [x] **Freeze the held-out test manifest.** Done 2026-10-16 4:00 PM PT (Danny go 3:55 PM PT): 273 ids, sha256 a03c8619…; recorded in docs/v2/G5_PREREG_EVAL.md (PR #33), tag v2-test-freeze-2026-10-16. The 15 quarantined gold rows stay out of test. Readiness: READY (G1 273, 37/37 test terms; T2 318/300). Nothing runs on the Sparks until Danny says go.
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
- [x] **Open items (Danny 2026-10-16 4:03 PM PT).** Held family calls applied; family gate reported as 16 (one private family excluded from H3 claims); betting-sharp stays retired; meaning/dictionary rows added for 65 new terms; formation tags accepted; 80-row label audit queued for Danny. Test manifest a03c8619 unchanged; readiness still READY.
