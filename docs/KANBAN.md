# Hyperlex v2 kanban (steps to data READY)

Updated 2026-10-16 12:35 PM PT. Mirrors:
- Notion board: https://app.notion.com/p/f57ad22c76d7436c9e024229be560a8e
- GitHub Project: https://github.com/orgs/Zero-State-LLC/projects/28 (Column field)
- Obsidian: `Projects/Hyperlex v2 board.md`

The Obsidian board is the source of truth. This file carries no slur terms, post text or private rows.

## Backlog
- [ ] **Hold-out supply for the test split.** Owner: Danny (decision). Only 19 test-split terms have observations and nearly all are at the 10-gold-per-term limit; 21 test terms have none. Options: (a) raise the 10-gold limit and the 3-per-queue cap for test terms (about 25 rows per queue under the 3 cap; 179 unruled rows exist on full terms); (b) authorize collection for the 21 empty test terms; (c) move families into the test split.

## Next
- [ ] **Danny decisions on families (private).** Owner: Danny. 1 Kimi low-confidence item (cockmonger: vulgar-insult vs nsfw-sexual) and 4 held terms from the new-row sort (2 possible slurs, 1 possible slur pun, 1 low confidence); held terms are named in the private store only. 63 rows stay unfamilied until then.
- [ ] **15 quarantined gold rows.** Owner: Danny (decision). Ruled gold rows (3 test, 2 val, 10 train) fail the existing DQ checks (author id present plus suspect synthetic source id). Fix the check, or keep them out.

## In progress
- [ ] **Raise test gold to 250 (G1), then 470 (G5).** Owner: Danny (rulings), Grok Bot (queues). Export 156/250 (landing 159). Queue 2026-10-16b built: 3 test rows (supply-limited, see Backlog).
- [ ] **PR #31: T026/T028 (windowed export context, R statuses non-gold, Jev use_mention).** Owner: Danny (merge yes). Opus review findings fixed; 42 tests pass.

## Blocked
- [ ] **Freeze the held-out test manifest.** Owner: Grok Bot, with Danny's sign-off. Blocked on G1 reaching 250.
- [ ] **Archive repo is read-only (scrimshawlife-ctrl/Hyperlex).** Owner: Danny. Decide: unarchive it, or move VERDICT-RULES into this repo.

## Done
- [x] **Rebuild the training export** (2026-10-16 12:30 PM PT). Row status, use_mention and excerpt provenance carried; R statuses out of gold and SFT; windowed context. Store 9,523 rows; gold test 156 / val 158 / train 933; overlaps 0. Author/community backfill re-run (author 15.1%, platform 100%, sub 88.0%).
- [x] **Family review: 8 items via Kimi** (moonshotai/kimi-k3). 7 settled (two private families vulgar-insult and nsfw-sexual, 2 terms to noise, 1 to general-slang, slur borderline kept borderline); 1 low-confidence item to Danny.
- [x] **Sort the 358 unfamilied rows.** Done via the Kimi verdicts plus an Opus sort of new rows (15 terms assigned, 6 to noise, 4 held). Assignments live in the private overlay.
- [x] **T026 export windowing and T028 Jev use_mention** coded with tests (PR #31, unmerged).
- [x] **Betting-sharp replacement pick.** Retired in PR #27 (220c108).
- [x] **Spec 009 Q1-Q5 decisions applied, and the repair queue re-ruled** (2026-10-16).
- [x] **Merge specs 008 and 009 to main.** #28 squash d87e3af, #29 squash 4f17542.
