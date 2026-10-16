# Hyperlex v2 kanban (steps to data READY)

Updated 2026-10-16 12:20 PM PT. Mirrors:
- Notion board: https://app.notion.com/p/f57ad22c76d7436c9e024229be560a8e
- GitHub Project: https://github.com/orgs/Zero-State-LLC/projects/28 (Column field)
- Obsidian: `Projects/Hyperlex v2 board.md`

The Obsidian board is the source of truth. This file carries no slur terms, post text or private rows.

## Backlog
- [ ] **Sort the 358 unfamilied rows.** Owner: Danny. Left over from the PR #27 family change.

## Next
- [ ] **Rebuild the training export.** Owner: Grok Bot. The current export predates the 10-15 backfill, the repair re-ruling and the auto-reject audit move.
- [ ] **Family review: 8 items via Kimi.** Owner: Grok Bot (Kimi pass), Danny (final call).
- [ ] **T026 follow-up: excerpt windowing in all export paths.** Owner: Grok Bot. Check `export_splits` and the other excerpt consumers use the same window as the queue (spec 009).
- [ ] **T028: `use_mention` in the Jev sense labelling runtime.** Owner: Grok Bot. `metrics-rule-v1.5` / `rebuilt-sense-v2` are specced in spec 009, but the runtime doesn't produce the field yet.

## In progress
- [ ] **Raise test gold to 250 (G1), then 470 (G5).** Owner: Danny (rulings), Grok Bot (queues). 159/250 for G1 and 159/470 for G5 as of 2026-10-16.

## Blocked
- [ ] **Freeze the held-out test manifest.** Owner: Grok Bot, with Danny's sign-off. Blocked on G1 reaching 250 and the export rebuild.
- [ ] **Archive repo is read-only (scrimshawlife-ctrl/Hyperlex).** Owner: Danny. The VERDICT-RULES v1.5 push got a 403 because the repo is archived. v1.5 lives in `specs/009-ruling-label-taxonomy/verdict-rules-v1.5.md`. Decide: unarchive it, or move VERDICT-RULES into this repo.

## Done
- [x] **Betting-sharp replacement pick.** Retired in PR #27 (220c108); six lineage families added.
- [x] **Spec 009 Q1-Q5 decisions applied, and the repair queue re-ruled** (2026-10-16). 0 `TARGET_ABSENT` rows remain.
