# VERDICT-RULES `metrics-rule-v1.5`: use/mention split (amendment)

- **Status:** decided. Danny, 2026-10-16 11:36 AM PT: "Do as recommended." This applies the spec 009 Q3 recommendation.
- **Amends:** `Hyperlex-archive: docs/vernacular/VERDICT-RULES.md` `metrics-rule-v1.4`, §3, §4 (path C) and §9. That repo copy is updated locally, but publishing it to the archive remote needs its own push approval.
- **Bump reason (§8):** what counts as a slang-sense post changes, so thresholds are computed over a different base.

## §3 (replaces the v1.4 text)

Each post gets two labels.

1. A sense label from the Jev sense contract `rebuilt-sense-v2`: `SLANG_SENSE`, `OTHER_SENSE`, or `UNKNOWN` (top probability below 0.5).
2. A `use_mention` label: `USE` or `MENTION`.
   - A **MENTION** draws attention to the word itself: defining it, quoting it, asking what it means, or commenting on its form.
   - A definition embedded inside a genuine use is a **USE**. This follows the Wiktionary CFI "conveying meaning" rule.

**MENTION posts are labelled O at the ruling level** and are not slang-sense posts. Author, week, day, community and purity counts use **slang-sense USE posts only**.

## §4 path C (changed part)

`C_ATTESTED` requires at least 2 independent people explaining the term. These may now be:

- MENTION posts whose explanation matches the term's slang meaning, or
- definition-style posts or explainer accounts, as before.

MENTION posts never count toward:

- the at least 3 slang-sense authors,
- the active weeks,
- the `LOW_SENSE_PURITY` numerator or denominator,
- paths A, B or D.

`attested_operator` and `attested_dictionary` are unchanged.

## §5 guards

The guards are unchanged. `SENSE_UNVERIFIED` treats a missing `use_mention` label as unlabelled.

## §9 version history (new row)

| Version | Date (PT) | Change |
|---|---|---|
| **v1.5** | 2026-10-16 11:36 | Use/mention split. MENTION is O at the ruling level, gets a separate `use_mention` field, and counts only toward path C's explainers (`C_ATTESTED`). Sense contract bumped to `rebuilt-sense-v2`. |

## Migration

- Labels from before v1.5 have no `use_mention` field. They are read as `USE` and stay valid under v1.4 until re-labelled.
- Verdicts computed under v1.4 keep their rule version. They are never silently recomputed (§8).

## Sources

- Wiktionary CFI, "Conveying meaning": https://en.wiktionary.org/wiki/Wiktionary:Criteria_for_inclusion
- Wilson, ACL 2012: https://aclanthology.org/P12-1067/
- Gligorić et al., NAACL 2024: https://aclanthology.org/2024.naacl-long.331/
