# Spec 009: Ruling label taxonomy (S / O / R / U)

- **Status:** DRAFT
- **Mode:** SHADOW. The ruling-tool changes in §5.3 are already in use on the operator box. Everything that touches VERDICT-RULES, Jev contracts or production verdicts is recorded only. It changes nothing until the operator promotes it (constitution VIII).
- **Stacked on:** spec 008 (PR #28).
- **Amends:** spec 008 CR-5 (see CR-B).
- **Depends on:** constitution, 007, 008.
- **Date:** 2026-10-16 PT.
- **Promotion:** Danny only (constitution VIII).

This spec contains no post text, no author handles and no private-list terms. Private-list rows are referenced only as "a private-list term (queue row `<date>:<row>`; `safety.private_overlay_ref`)". Where the row number is held only in the private store, it is written `NNN`.

## 1. Summary

The ruling queue uses four codes: S, O, R and U. Until now their meaning lived in scattered ruling notes, and one tool path read them as term-level judgements. This spec does four things:

1. It fixes the meaning of each code.
2. It states that every label is an **excerpt-level adjudication**, never a lexical promotion or rejection.
3. It records the sense rules Danny applied on 2026-10-13 and 2026-10-16.
4. It specifies the corrections-only reply protocol that is now implemented.

It also resolves conflicts with VERDICT-RULES v1.4, spec 008 and the decision log (CR-A to CR-K).

## 2. Scope

**In scope:**
- Ruling code semantics.
- Row-level sense rules.
- The reply protocol: corrections-only, multi-part replies and in-place update.
- The auto-reject gate.
- Provenance fields.
- The location of the tooling.
- How historical rows are treated.

**Out of scope:**
- Verdict thresholds.
- Evidence paths.
- Family structure.
- Overlay membership.
- Any reinterpretation of past rulings.

## 3. Label taxonomy

Danny's definitions (2026-10-16 training notes) are quoted verbatim.

| Code | Stored value | Definition (verbatim) | Gold? |
|---|---|---|---|
| **S** | `SLANG_SENSE` | "slang (contextual slang usage)" | Yes |
| **O** | `OTHER_SENSE` | "ordinary meaning, including proper names and established non-slang usage" | Yes |
| **R** | `REJECT` | "target absent from the visible excerpt" | No |
| **U** | `UNSURE` | "unresolved sense, meaning or referent" | No |

- Gold is S and O only.
- R and U rows are never gold and never training labels. This matches the G5 exclusion of UNSURE and REJECT, which is unchanged.

## 4. Data as of 2026-10-16

**2026-10-16 queue, first pass (applied 11:02 AM PT):**
- 17 Danny corrections, plus 283 unlisted rows kept at the model label.
- 300 rulings: S 181, O 114, R 5, U 0.

**Training corrections, parts 1–3 (applied 11:15 AM PT):**
- 74 rows listed.
- 73 rows changed in place. No duplicates were created.

**Queue now:**
- S 177, O 90, R 24, U 9 (total 300).
- Listed rows: 91 (17 + 74).
- Retained rows: 209.

## 5. Functional requirements

### 5.1 Label semantics

- **FR-001** The ruling tool accepts exactly S, O, R and U. It stores them as `SLANG_SENSE`, `OTHER_SENSE`, `REJECT` and `UNSURE`. Any other code aborts the apply.
- **FR-002** Only S and O rows are gold. R and U rows are kept for audit and are excluded from gold, training labels and evaluation (G5 unchanged).
- **FR-003** Every label is an excerpt-level adjudication of one occurrence. A label never writes, implies or stands in for any term-level state. This covers lexical promotion, rejection, QUARANTINE, HOLD, PASS, `operator_term_status` and private-overlay membership. A retained or listed S marks contextual slang usage only (Danny, 2026-10-16).
- **FR-004** No term-level rejection follows from R rows.
  - **The bug.** On 2026-10-16, a batch whose only row for a common internet term ("normie") was R wrote `operator_term_status=rejected` for that term. Earlier queues held gold S rulings for the same term.
  - **The fix (implemented).** Auto-reject is off by default. It runs only with `--auto-reject-terms`. Even then, it fires only if **every** ruling for the term in the landing file, across all queue dates, is R.
  - **Recommendation.** Under this taxonomy, R means only that the target was not visible. So even an all-R history is not evidence against the term. Operators SHOULD NOT use `--auto-reject-terms`. Its removal waits on Q1.
- **FR-005** The existing `operator_term_status=rejected` row for "normie" is left in place, neither deleted nor overwritten, until Danny decides (Q1).

### 5.2 Sense rules (row level)

- **FR-006 Per-occurrence sense.** A term's label is decided for each occurrence. The same term may be S in one row and O in another.
  - Example: *cracked* is O at 2026-10-16:074 (a beer was opened) and S at 2026-10-16:261 (exceptionally good).
  - No term-level sense is assumed when ruling (see CR-K).
- **FR-007 Use/mention.** A term that is being defined, quoted or discussed as a word (mentioned, not used) is O.
  - Example: a private-list term (queue row 2026-10-16:204; `safety.private_overlay_ref`) is being defined, so it is O.
  - Proposed: a separate `use_mention` field (`USE` / `MENTION`) records the distinction (CR-A).
- **FR-008 Clinical vs insult.** A clinical, descriptive or technical use of a term that also has an insult sense is O. Use as an internet insult is S.
  - Example: a private-list term (queue row 2026-10-16:296; `safety.private_overlay_ref`) appears in a clinical distinction, so it is O.
- **FR-009 Derogatory internet labels.** A derogatory internet label in insult use is S.
  - Examples: *incel*; *chud*; a private-list term (queue row 2026-10-16:NNN; `safety.private_overlay_ref`); row 2026-10-16:205.
  - Stylized mocking usage is also S: a private-list term (queue row 2026-10-16:NNN; `safety.private_overlay_ref`).
  - Offensiveness is a separate axis, handled by the safety overlay. It never changes the S/O decision, and S never changes overlay state (CR-G).
- **FR-010 Domain jargon vs subcultural coinage.** Apply these three branches in order:
  1. **Field-literal jargon = O.** An established technical, hobby or trade term used for its field-literal referent, in the field's ordinary descriptive register, is O. Examples: *playerbase*, and *buffed* at 2026-10-16:004.
  2. **In-group coinage = S.** A subcultural in-group coinage working as informal or expressive vocabulary is S, especially when it is used outside formal registers or has spread beyond its origin community. Example: *headcanon* at 2026-10-16:003 and 2026-10-16:198, consistent with Danny's S.
  3. **Unclear = U.** If the excerpt cannot show which branch applies, the row is U.

  The basis and limits of this rule are in CR-J and research.md R-1. The boundary is not yet confirmed (Q4).
- **FR-011 Proper names and products are O.** Example: *grok* names the AI product, so it is O.
- **FR-012 Foreign-language collisions are O.**
  - Example: *algo* in the Spanish "o algo" ("or something") is O (2026-10-16).
  - Example: *algo* as short for "algorithm" was ruled O at 2026-10-13:142 (Danny, 2026-10-13).
- **FR-013 U.** U means the sense, meaning or referent is unresolved, so more context is needed. Examples include 2026-10-16:021, :080, :131, :170, :208, :257, :277 and :292. U also still covers deliberately meaningless memes, stored as U and capped at OBSERVE (CR-E).
- **FR-014 R.** R means the target is absent from the supplied or visible excerpt, including truncated excerpts.
  - R is a row-level extraction fact, not a lexical judgement.
  - A forward R row maps to row status `EXCLUDED_INVALID`, is kept for audit, and is never a term-level rejection (CR-B).
  - An R row never counts as an attested occurrence (CR-I).

### 5.3 Reply protocol (implemented)

- **FR-015 Corrections-only detection.** A reply whose header is "Corrections only" is detected automatically. The `--corrections-only` flag forces this mode. `--no-auto-corrections` turns automatic detection off.
- **FR-016 Answer modes.** In corrections-only mode:
  - Rows the reply lists get Danny's label and `answer_mode=corrections_only_listed`.
  - Unlisted rows keep the model's proposed label and get `answer_mode=corrections_only_retained`.
- **FR-017 Provenance of retained labels (DEC-010).**
  - A retained label is gold **only** because the human explicitly ratified "all unlisted rows retain the model's proposed labels" for that queue. The model proposes. The human act creates the ground truth.
  - Each retained row MUST record `answer_mode=corrections_only_retained` and the answer file that carried the ratification (`revision_source`, or `ratification_ref` once added, T018).
  - Without an explicit ratifying header or flag, unlisted rows get no ruling (CR-H).
- **FR-018 Multi-part replies.** One queue date may be answered by several files and/or by "PART n:" comma lists. All parts are merged into one apply.
- **FR-019 Duplicate indices.** The same index with the same label collapses to one entry. The same index with conflicting labels aborts the whole apply, and nothing is written.
- **FR-020 Update in place.**
  - `--update-existing` upserts rulings in place and records `revised_from` (prior label), `revised_at` and `revision_source`.
  - It never creates a duplicate row.
  - Re-applying the same files changes nothing.
- **FR-021 Dry run.** `--dry-run` reports `new`, `updated`, `unchanged`, `listed` and `retained` counts and writes nothing. `--write-sqlite` also writes the SQLite store.

### 5.4 Location of the tooling

- **FR-022** The canonical runtime copy is `hyperlex-v2-tracker/ruling_queue.py` on the operator box. It is not in the repo.
  - A mirror copy for review and CI lives at `scripts/v2/ruling_queue.py`, with tests at `tests/test_ruling_queue_v2.py`.
  - The tracker copy wins on any difference. Changes are made in the tracker first and copied to the mirror in the same session.

### 5.5 Historical rows and safety

- **FR-023** Legacy rows are never reinterpreted. This covers 2026-10-12 U-for-absent rows, R rows up to and including 2026-10-15 (008 CR-5), and existing auto-reject status rows (constitution VI).
- **FR-024** Known gap: the 2026-10-15 corrections-only queue was applied with listed rows only, so its unlisted rows have no ruling. They are not backfilled until Danny decides (Q2).
- **FR-025** The repo, PR text and this spec never name a private-list term. Such rows are referenced by queue id and `safety.private_overlay_ref` only (CR-G).

## 6. Success criteria

- **SC-001 (met).** Re-running the four 2026-10-16 answer files with `--update-existing --dry-run` yields new 0, updated 0, unchanged 300, listed 91, retained 209.
- **SC-002 (met).** The 2026-10-16 queue totals 300 rows: S 177, O 90, R 24, U 9.
- **SC-003 (met).** An apply with default flags writes zero `operator_term_status` rows.
- **SC-004 (met).** `tests/test_ruling_queue_v2.py` passes with 18 tests.
- **SC-005.** On the owner box, a check of all spec 009 files and the mirror against `HYPERLEX_PRIVATE_REGISTRY` finds zero matches.
- **SC-006.** Every `corrections_only_retained` row carries a reference to its ratifying answer file.
- **SC-007 (pending the 008 builder).** No R row is counted as an attested occurrence, and no candidate leaves `NOT_ATTESTED` on R rows alone.

## 7. Conflicts and resolutions

### CR-A Use/mention vs VERDICT-RULES v1.4 §3

- **Existing rule:**
  - VERDICT-RULES v1.4 §3 defines `SLANG_SENSE` as including "mentioning or explaining the slang".
  - Path C's `C_ATTESTED` counts "≥ 2 independent people in the corpus explaining the term".
- **Research basis:**
  - Gligorić et al. (NAACL 2024) separate mention (quoting, pointing out a word's properties) from use. They show that models conflate the two, and that teaching the distinction cuts false positives on counterspeech mentions by 82.61% (hate-speech setting). See research.md R-3.
  - Merriam-Webster: "No word, in fact, is invariably slang". The label belongs to an application in context (R-1).
- **Integration:**
  - At ruling level, a mention is O (Danny, 2026-10-16:204).
  - A separate `use_mention` field (`USE` / `MENTION`) is added to rows and to `jev_sense_contract`.
  - A row with `O` + `MENTION` whose explanation matches the slang sense may feed `C_ATTESTED`. It never counts toward slang-sense authors, active weeks or the paths' minimums.
  - Its treatment in `LOW_SENSE_PURITY` must be set by the same change.
  - This changes what §3 counts, so VERDICT-RULES needs a rule-version bump (§8). **Status: OPEN, not decided** (Q3). Until the bump, Jev's `SLANG_SENSE` keeps its v1.4 meaning, and ruling-level O + MENTION is recorded in SHADOW only.
- **Residual risk:**
  - Some posts both explain and use the term. The proposal is `USE` when any use is present. This is unvalidated.
  - Mentions of a different sense must not feed `C_ATTESTED`. The existing matching-sense rule still applies.

### CR-B R vs spec 008 CR-5 (amends 008)

- **Existing rule:**
  - 008 CR-5 (Danny, 2026-10-15 9:52 PM PT): historical R = `REJECTED`. Forward R = record invalid / `EXCLUDED_INVALID`. A new H = hold.
  - Danny on 2026-10-13 and 2026-10-16: R = target absent from the excerpt.
- **Research basis:** SemEval-2007 Task 07 excluded instances where no sense fits (2%) from scoring, rather than treating them as negatives (R-5). An excerpt with no target is likewise not data about the sense.
- **Integration:**
  - "Target absent" is a row-level record-invalid case.
  - Forward R rows (2026-10-16 onward) become `EXCLUDED_INVALID` **for the row**. They are kept for audit and are never a term-level rejection.
  - Historical R rows keep `legacy.ruling_code = R` with status `REJECTED`, as 008 decided. That status is read as row-scoped only. No term-level state is derived from it.
  - H stays as 008 defines it: term-level "not yet established". U is row-level "sense unresolved". The two are not interchangeable.
  - 008 CR-5 is amended to say this.
  - Historical term-level `operator_term_status='rejected'` rows written by the auto-reject path need operator review (Q1).
- **Residual risk:**
  - Whether forward R should get its own status (`TARGET_ABSENT`) rather than share `EXCLUDED_INVALID` is open (Q5).
  - Sharing a status mixes extraction failures with non-innovations in audits.

### CR-C 2026-10-12 "target absent → extraction repair" (stored as U)

- **Existing rule:**
  - On 2026-10-12, absent-target rows were stored as U and routed to extraction repair.
  - From 2026-10-13, absent-target rows are R. The repair list is `rulings/repair/2026-10-13-target-absent.txt`.
- **Research basis:** n/a. This is receipt integrity (constitution VI).
- **Integration:**
  - Legacy U-for-absent rows are not reinterpreted as R.
  - Repair files remain and stay the route to re-extraction.
  - A repaired row is re-queued as a new ruling. It is not edited in place.
- **Residual risk:** U counts before 2026-10-13 include extraction failures. Analyses of U rates must split at 2026-10-13.

### CR-D Proper names vs VERDICT-RULES QUARANTINE

- **Existing rule:** QUARANTINE (term level, decided by Jev) covers a proper name, or only an ordinary non-slang sense.
- **Research basis:**
  - Merriam-Webster labels attach to single senses (R-1, R-2).
  - Jev's `OTHER_SENSE` already lists "a name, school, company, ticker".
- **Integration:**
  - A row-level O for a proper name (FR-011) is consistent with this.
  - Term-level QUARANTINE is still decided by Jev under the rules. It is never inferred from O rows, even all-O rows (FR-003).
- **Residual risk:** none new.

### CR-E DEC-004 meaningless memes

- **Existing rule:** DEC-004 caps "67" at OBSERVE. The row was stored as U (2026-10-13 note, row 102).
- **Research basis:** n/a.
- **Integration:** Unchanged. U covers "meaning unresolved or null", and the term-level cap is still `SLANG_NULL_MEANING` → OBSERVE.
- **Residual risk:** U mixes "unknown" with "known to be meaningless". The term-level verdict carries the difference.

### CR-F DEC-005 and the 2026-10-15 fold decision

- **Existing rule:**
  - DEC-005: "brain rot aura" is a mutation.
  - DEC-HLX-v2-2026-10-15 #1: brainrot-aura and ai-native stay separate families.
- **Integration:** The taxonomy labels occurrences. It does not create, merge or split families. **No conflict.**
- **Residual risk:** none.

### CR-G Private-list terms

- **Existing rule:**
  - DEC-HLX-v2-2026-10-15 #3: slur-tagged rows may be used in private training only.
  - 008 CR-11: nothing in the repo names a slur-list term. Records use `surface_sha256` and `safety.private_overlay_ref`.
- **Research basis:** n/a. This is a safety rule.
- **Integration:**
  - S on a private-list term row means contextual usage only.
  - It never implies promotion.
  - Overlay membership is unchanged by any S/O/R/U label.
  - The repo references such rows by queue id only.
- **Residual risk:** Row ids plus queue dates could be joined with the private store. That join happens only on the owner box.

### CR-H DEC-010 vs corrections-only retained labels

- **Existing rule:** DEC-010 says models never create ground truth.
- **Research basis:** SemEval-2013 Task 11 uses human adjudication as the source of final labels (R-4). Under this protocol, the human act is the ratification.
- **Integration:**
  - A retained label becomes gold only through Danny's explicit ratification that "all unlisted rows retain the model's proposed labels".
  - The ratification is recorded per row (FR-016, FR-017).
  - A reply without the header or flag ratifies nothing.
  - DEC-010 holds: the model proposed and the human decided.
- **Residual risk:**
  - Blanket ratification of 209 rows is weaker review than an explicit ruling on each row.
  - `answer_mode` lets analyses separate the two groups or weight them differently.

### CR-I R rows vs 008 `NOT_ATTESTED`

- **Existing rule:** 008 `NOT_ATTESTED` means a discovery hit with 0 stored occurrences. Q5 kept 8 holds at `NOT_ATTESTED`.
- **Integration:**
  - An R row is not an occurrence of the target, so it is never counted as attested.
  - R rows alone never move a candidate out of `NOT_ATTESTED`.
- **Residual risk:** The 008 cohort builder must enforce this (SC-007).

### CR-J Domain-jargon rule vs "fandom vocabulary" + S

- **Existing rule:**
  - *playerbase* and *buffed* are ruled O as gaming terminology.
  - *headcanon* is called "fandom vocabulary" yet ruled S (2026-10-16:003, :198).
- **Research basis:**
  - Merriam-Webster's slang label covers words "usually not limited to a particular region or area of interest" (R-1).
  - OED-style labelling keeps subject (field) labels separate from register labels (R-6).
  - So field jargon used within its field is a subject matter, not slang.
  - The sources do not settle whether an in-group coinage counts as slang when it is used inside its group.
- **Integration:**
  - FR-010 places *playerbase* and *buffed* in branch 1: field-literal referent, descriptive register.
  - It places *headcanon* in branch 2: a coinage working as informal in-group vocabulary. This matches Danny's S.
  - Remaining for Danny (Q4):
    - whether branch 2 applies when a coinage is used **inside** its origin community in a plain descriptive way;
    - whether spread beyond the field is required for S.
  - The cited sources do not establish how far *headcanon* has spread.
- **Residual risk:**
  - The split between "established jargon" and "coinage" is a judgement.
  - Expect U or disagreement on hobby terms until Q4 is answered.

### CR-K Per-occurrence sense vs "one coherent meaning"

- **Existing rule:**
  - VERDICT-RULES §1: PASS requires "one coherent meaning".
  - §3 excludes `OTHER_SENSE` posts from evidence.
  - §5 `LOW_SENSE_PURITY` blocks PASS.
- **Research basis:**
  - SlangNet: conventional and slang senses of one form coexist (R-8).
  - Pei, Sun & Xu: slang usage of existing words is identified per token (R-7).
- **Integration:**
  - Per-occurrence labels are consistent with these rules.
  - PASS still needs one coherent slang meaning across S posts.
  - O rows of other senses are excluded as `OTHER_SENSE` is today.
  - The `LOW_SENSE_PURITY` guard still applies.
- **Residual risk:** Two distinct slang senses of one form both receive S. Separating them is Jev's job (§1 HOLD on unrelated senses), not the ruling label's job.

## 8. Open questions for Danny

- **Q1.** Keep or delete the "normie" `operator_term_status=rejected` row? Should other historical auto-reject rows be audited? Should `--auto-reject-terms` be removed?
- **Q2.** Should the unlisted rows of the 2026-10-15 corrections-only queue be backfilled at the model label (as `corrections_only_retained`, citing that reply), or left without a ruling?
- **Q3.** Should VERDICT-RULES be bumped for the use/mention split? If so, do `O` + `MENTION` explainer rows count toward `C_ATTESTED`, and how are they treated in `LOW_SENSE_PURITY`?
- **Q4.** Confirm the headcanon-class boundary. Is an in-group coinage S even when used inside its own community, and is spread outside the community required?
- **Q5.** Should forward row-level R map to 008's `EXCLUDED_INVALID`, or to a distinct `TARGET_ABSENT` status?
