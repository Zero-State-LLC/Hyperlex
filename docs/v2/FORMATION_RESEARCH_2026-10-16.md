# Research: making word formation a first-class signal in Hyperlex (draft input)

Prompt: Danny, 2026-10-16 3:07 PM PT: "Model needs to know how slang forms anyways. Otherwise how to predict? Look at what we have already and research how we can extend Hyperlex with this as a consideration."

Status: research input only. No state changes beyond the approved formation field. **Citations are from memory and are unverified.** No model or literature-search spend was used, because the session spend cap had already been passed. Check the DOIs and venues before anything is promoted.

## (a) What Hyperlex already has
| Asset | Formation / prediction content | Gap |
|---|---|---|
| Spec 001, mutation grammar (`specs/001-mutation-grammar`) | "Slang is a productive grammar." Operator-stack detection (`mutation_trace.v0.1`), lineage `branch_operator` (finished history) and `mutation_prediction.v1` (future forms of a slang atom) | Operators are detector-side (adversarial rewrites). They are not tied to the v2 data or labelled as formation types. |
| Spec 008, lexical emergence (PR #28, merged) | Observe from the first attestation. Adoption, diffusion and persistence are outcomes to measure | Formation is not modelled as a driver of emergence or diffusion. |
| v2 T1 (sense) / T2 (meaning) / T3 (lineage family) | Families group terms by register and community (e.g. `-maxxing` sits in brainrot-aura by family, not by mechanism) | There is no mechanism label. Families mix mechanisms. |
| Spec 007, Hyperlexical model, and the rc3 history (pointer/copy head) | A copy/pointer head over the input span, aimed at surface reuse | The rc3 notes weren't found on main today. Re-check the archive. A copy head is a natural fit for clipping, affixation and respelling, where the output reuses parts of the input. |
| Vernacular discovery (`run_discover.py`) and the T2 discovery pass (`discovery/discover_pass.py`) | Finds new candidate terms from posts | There is no prior over likely forms. A formation-aware filter could rank candidates such as productive affixes. |
| New: `terms.formation_json` plus the export `formation` field | 366 terms tagged across 11 mechanisms | The tags are INFERRED (Opus) and await Danny's corrections. |

## (b) Literature
- **Morphological productivity.** Baayen (1992, *Yearbook of Morphology*) and Baayen (2009, in *Corpus Linguistics: An International Handbook*) use hapax-based productivity, P = n1/N, to measure which affixes are actively coining. It applies directly to `-maxxing`, `-pilled`, `-core` and `-gender`. See also Plag (2003) and Bauer (1983, 2001 *Morphological Productivity*).
- **Blends and clippings.** Gries (2004, *Linguistics*) studies blend structure. Deri & Knight (2015, NAACL) generate portmanteaus with FSTs. Kulkarni & Wang (2018, NAACL, "Simple models for word formation in slang") cover blends, clippings and reduplicatives.
- **Eggcorns.** Liberman (2003, Language Log) and the Eggcorn Database (eggcorns.lascribe.net) treat these as reanalysis. They are rare in our data (1 tag).
- **Emergence and diffusion.** Grieve, Nini & Guo (2018, *Journal of English Linguistics*) map lexical innovation on American Twitter. Grieve et al. (2017, *English Language and Linguistics*) analyse lexical emergence online. Eisenstein, O'Connor, Smith & Xing (2014, *PLoS ONE*) study the diffusion of lexical change on social media. Ryskina et al. (2020, SCiL) find that neologisms are born in sparse semantic neighbourhoods.
- **LLMs and novel words; wug tests.** Berko (1958, *Word*) is the original wug test. Weissweiler et al. (2023, EMNLP) test ChatGPT's morphology on wugs. Hofmann et al. (2020, EMNLP, DagoBERT) generate derivational morphology. Hofmann et al. (2021, ACL) show that tokenisation hurts handling of derivations. Schick & Schütze (2019/2020) estimate embeddings for rare words.
- **Compositional generalisation.** SCAN (Lake & Baroni 2018, ICML), COGS (Kim & Linzen 2020, EMNLP) and CFQ (Keysers et al. 2020, ICLR) hold out recombinations. The same logic gives a held-out formation axis.
- **Slang generation and interpretation.** Sun, Zemel & Xu (2021, TACL, "A computational framework for slang generation"), plus Sun et al. 2019 (CogSci) on slang as categorisation. Ni & Wang (2017, IJCNLP) on explaining non-standard words and phrases. Wilson et al. (2020, LREC) on Urban Dictionary embeddings.

## (c) Extension options
| Option | Data | Specs | Eval | Readiness effect | Cost | Risks |
|---|---|---|---|---|---|---|
| 1. **Formation label as an auxiliary task** (multi-label head next to T1) | Already have 366 term tags; needs Danny's corrections (2026-10-16g) | Add to spec 009 / G5 as exploratory | Macro-F1 per type on test terms; does T1 improve with the auxiliary head? | None if kept exploratory | About $0 (tags exist); small Spark compute | Term-level labels repeat across rows, so the head can memorise the term. Keep it term-split (it already is). |
| 2. **Formation-conditioned held-out** (unseen productive affix or mechanism as a split axis) | Pick 1–2 affixes (e.g. -gender, -core) whose terms are all in test | New split axis in G5; must not move existing splits, so only *report* a slice over existing test terms, or pre-register for v3 | T1 accuracy on test terms grouped by formation type, as a report-only slice | None if report-only. A real re-split would change the manifest, so defer it | $0 | The slices are small (37 test terms), so CIs will be wide. Use the term-level bootstrap. |
| 3. **Generation / prediction task** (base + mechanism → form, or form → base + mechanism + meaning) | Needs base words: derivable for clipping, blend and affixation (about 145 terms) | New task T6 (or a spec 001 `mutation_prediction.v1` bridge) | Exact or edit-distance match on held-out terms; human plausibility ratings | Separate track; doesn't block G1–G5 | Labelling bases is about $0.10–0.30 at Flash cost; eval needs human review | Synthetic leakage if generated forms are fed back as data. Keep generated forms out of the observation store. |
| 4. **Wug-style synthetic probes** (nonce bases with real affixes, e.g. "blorpmaxxing") | Templated probe set, about 200 items | Probe-only appendix to G5 | Does the model assign the affix sense to nonce words? Compare BASE vs LoRA | None. Probes are never training data | About $0 to make; inference on Spark | Contamination if probes leak into train. Store them in a separate file, hash it, and add a fail-closed guard in `train_lora`. |

## Recommendation (smallest useful path, no readiness delay)
1. Now: keep the formation field as metadata (done). Danny corrects 2026-10-16g along with the 16m rulings.
2. G5 (no gate change): add **report-only** formation slices of T1 test accuracy and a wug probe set as exploratory analyses. Pre-register them in the G5 doc so they don't count as peeking. This needs no re-split and no manifest change.
3. After G5: add the auxiliary formation head (option 1) and productivity tracking (Baayen P per affix over time), which ties into spec 008 diffusion.
4. v3: a formation-held-out split (option 2) and a generation task (option 3), linked to spec 001 `mutation_prediction.v1`.
