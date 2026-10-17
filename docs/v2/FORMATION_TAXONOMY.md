# Hyperlex v2: word-formation (mechanism) field

Status: DRAFT. Approved by Danny on 2026-10-16 at 3:06 PM PT. This is a term-level attribute. It is **not** a lineage family and it does **not** drive the split.

## Schema (backward-compatible)
- `terms.formation_json` is a nullable TEXT column holding `{"types": [..], "confidence": "high|medium|low", "basis": "...", "note": "..."}`. A term may carry more than one type.
- The export adds `formation: [..]` to each row and writes `[]` when the field is absent. Consumers must tolerate the key being missing or empty: `train_lora.load`, `prereg_eval` and `base_audit` all ignore it.
- `basis` records where the tag came from: `INFERRED:opus formation tag 2026-10-16`, or a Danny ruling (`algo` = clipping, 2026-10-16 3:04 PM PT, "example of symbolic compression").

## Types
| Value | Definition | Example |
|---|---|---|
| clipping | A word shortened, keeping one part | algorithm → algo |
| blend | Parts of two words fused, usually with overlap | brunch, frenemy |
| acronym_initialism | Built from the initial letters of a phrase | fr, icl, kys |
| eggcorn | A misheard or reinterpreted phrase that makes local sense | "for all intensive purposes" |
| compound | Two or more whole words joined | slop grenade |
| affixation | A productive prefix or suffix | -maxxing, -pilled, -core, -gender |
| semantic_shift | An existing word with a new sense (broadening, narrowing, metaphor) | cooked, mid, sharp |
| borrowing | Taken from another language or dialect | izzat |
| phonetic_respelling | A spelling that reflects pronunciation or accent | dutty, finna |
| coinage_other | Invented outright, or another process | — |
| unknown | The type can't be told from the evidence | — |

## Sources
- Bauer, L. (1983). *English Word-Formation*. Cambridge University Press.
- Plag, I. (2003). *Word-Formation in English*. Cambridge University Press. Covers clipping, blending, affixation, compounding and conversion.
- Baayen, R. H. (1992). Quantitative aspects of morphological productivity. *Yearbook of Morphology 1991*, 109–149. Productivity measure P = n1/N.
- Gries, S. Th. (2004). Shouldn't it be breakfunch? A quantitative analysis of blend structure in English. *Linguistics* 42(3).
- Liberman, M. (2003). "Egg corns: folk etymology, malapropism, mondegreen, ???" Language Log, 23 Sep 2003. This is where Pullum's coinage "eggcorn" was introduced. See also the Eggcorn Database (eggcorns.lascribe.net).

These citations are from memory. Verify the DOIs and pages before the spec is frozen.

## Tagging, 2026-10-16
- Opus tagged all 366 terms in batches of 40. Danny ruled `algo` as clipping.
- Tag counts: compound 114, semantic_shift 110, affixation 65, clipping 46, blend 34, acronym_initialism 29, borrowing 25, phonetic_respelling 25, coinage_other 21, unknown 20, eggcorn 1.
- 118 terms carry more than one type. Confidence: 175 high, 126 medium, 65 low.
- The corrections-only review list is in the private tracker. Slur-family terms are in a separate private file and appear here only as counts.
