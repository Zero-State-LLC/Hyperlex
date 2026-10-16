# Spec 009 research: ruling label taxonomy

Date: 2026-10-16. Only the sources listed in §3 are used. Where they do not settle a point, this file says so.

## 1. Findings

### R-1 Slang is a label on a word in context, not on a word form

**Source:** Merriam-Webster, Explanatory Notes: usage labels.

**What it says:**
- The slang label is used for words "especially appropriate in contexts of extreme informality, that are usually not limited to a particular region or area of interest".
- "There is no satisfactory objective test for slang, especially with reference to a word out of context. No word, in fact, is invariably slang, and many standard words can be given slang applications."
- The label can attach to a single sense.
- Disparaging and offensive are separate stylistic labels.

**Supports:**
- Per-occurrence labelling (FR-006).
- Ruling from context rather than from the word list (FR-003).
- Field jargon used within its field is not slang (FR-010, branch 1).
- Offensiveness is a separate axis from S/O (FR-009).

**Does not settle:** Whether a fandom or community coinage counts as slang when it is used inside that community. "Usually not limited" is a tendency, not a test.

### R-2 Sense-level slang labels

**Source:** Merriam-Webster thesaurus usage labels.

**What it says:** The slang label is applied to individual senses or entries, not to every use of the spelling.

**Supports:** CR-D (a row-level O for a name does not decide the term) and CR-K.

### R-3 Use vs mention

**Source:** Gligorić, Cheng, Zheng, Durmus, Jurafsky, NAACL 2024.

**What it says:**
- Mention (quoting a word, or pointing out its properties) is distinct from use.
- NLP systems conflate the two, which leads them to censor counterspeech.
- Teaching the distinction cut false positives on counterspeech mentions by 82.61% in the hate-speech setting.

**Supports:**
- O for a defined or quoted term (FR-007, row 2026-10-16:204).
- An explicit `use_mention` field, so that models are taught the distinction rather than left to infer it (CR-A).

**Does not settle:**
- Whether explainer mentions should count as attestation. That is a VERDICT-RULES policy choice (Q3).
- The study's domain is hate speech and misinformation, not slang in general.

### R-4 Per-instance tagging with an inventory plus a catch-all, and adjudication

**Source:** Navigli et al., SemEval-2013 Task 11.

**What it says:**
- Instances are tagged one by one against a sense inventory that includes an OTHER catch-all.
- Three annotators took part. Fleiss' kappa was 0.66. Disagreements were adjudicated.

**Supports:**
- The S/O design: S is the target sense class and O is a catch-all for every other sense, name or language.
- Human adjudication as the source of final labels (CR-H).

**Does not settle:** Agreement for our scheme. The queue has a single adjudicator, so we have no kappa. This is a residual risk, not a finding.

### R-5 Unfit instances are excluded, and agreement depends on granularity

**Source:** Navigli, Litkowski, Hargraves, SemEval-2007 Task 07.

**What it says:**
- Instances where no sense fits (2%) were excluded.
- Inter-annotator agreement depends on how fine-grained the sense inventory is. Agreement was 93.8% with a coarse inventory.

**Supports:**
- R and U rows are excluded from gold rather than counted as negatives (FR-002, CR-B).
- A coarse two-way gold split (S/O) is easier to agree on than a fine-grained one.

### R-6 Register labels are separate from subject labels

**Source:** Quick and Dirty Tips on dictionary labels. This is a secondary source describing OED practice.

**What it says:** The OED keeps register labels (slang, derogatory, offensive) separate from subject or field labels.

**Supports:**
- Field membership (gaming, fandom) is not itself slang (FR-010).
- Derogatory is a register property alongside slang, not a replacement for it (FR-009).

**Caveat:** This is secondary. It is not a direct citation of the OED.

### R-7 Token-level slang, including slang use of existing words

**Source:** Pei, Sun & Xu, CoNLL 2019, "Slang Detection and Identification".

**What it says:**
- Slang is identified at the token level.
- Novel-word slang is distinguished from slang usage of an existing word (for example, "the band's album is sick").

**Supports:**
- *cracked* S at 2026-10-16:261 vs O at 2026-10-16:074 (FR-006).
- Novel forms such as *kek* are S in use.

### R-8 Conventional and slang senses of one form coexist

**Source:** Dhuliawala, Kanojia, Bhattacharyya, LREC 2016, SlangNet.

**What it says:** One word form can carry both a conventional and a slang sense (sick = ill / awesome).

**Supports:** CR-K. A term can have O rows without contradicting a coherent slang meaning on its S rows.

### R-9 Background only

**Source:** Wilson et al., LREC 2020, Urban Dictionary Embeddings.

**Use:** Background on Urban Dictionary as a crowd-sourced slang resource. No rule in spec 009 depends on it.

## 2. What the sources do not settle

- **The headcanon class (Q4).** The sources support "field jargon is not slang". They do not say how to treat in-group coinages used inside their group, or how much spread is needed. The rule in FR-010 is a proposal that fits Danny's rulings. It is not a sourced test.
- **Mentions as attestation (Q3).** This is a policy question.
- **How R maps to a status (Q5).** This is a schema choice. The sources only support excluding R rows from scoring.
- **Agreement for this scheme.** There is no second annotator, so agreement is unmeasured.

## 3. Sources

- Merriam-Webster, Explanatory Notes, usage labels: https://www.merriam-webster.com/help/explanatory-notes/dict-usage
- Merriam-Webster, thesaurus usage labels: https://www.merriam-webster.com/help/explanatory-notes/thes-usage-labels
- Quick and Dirty Tips, dictionary labels (secondary, on OED practice): https://www.quickanddirtytips.com/articles/dictionary-labels/
- Gligorić, Cheng, Zheng, Durmus, Jurafsky, NAACL 2024, "NLP Systems That Can't Tell Use from Mention Censor Counterspeech, but Teaching the Distinction Helps": https://aclanthology.org/2024.naacl-long.331/
- Navigli et al., SemEval-2013 Task 11: https://aclanthology.org/S13-2035.pdf
- Navigli, Litkowski, Hargraves, SemEval-2007 Task 07: https://aclanthology.org/S07-1006.pdf
- Pei, Sun & Xu, CoNLL 2019, "Slang Detection and Identification": https://www.researchgate.net/publication/336997994_Slang_Detection_and_Identification
- Dhuliawala, Kanojia, Bhattacharyya, LREC 2016, SlangNet: https://aclanthology.org/L16-1686.pdf
- Wilson et al., LREC 2020, Urban Dictionary Embeddings: https://aclanthology.org/2020.lrec-1.586/
