# Hyperlex v2 — G5 preregistered evaluation (draft)

Status: DRAFT preregistration. Freeze (hash this file + test manifest) **before** any training run. SHADOW-only.

## Hypotheses
- H1 (T1): LoRA-tuned Nano 8B beats BASE on T1 sense accuracy on the hashed grouped test split. Term-level paired bootstrap (resample test **terms** with replacement, all of a term's rows together; 10k resamples, seed 7); two-sided 95% CI on the accuracy difference, reject H0 if the CI excludes 0 (alpha=0.05).
- H2 (T1): LoRA beats bag-of-terms (logistic regression on term+context unigrams) and the rule baseline (`observation_sense_v1`). Same term-level paired bootstrap each, Holm correction across the 3 comparisons.
- Why term-level, not row-level McNemar: test rows are clustered within ~37 terms (cap 10 gold/term), so rows are not independent; row-level McNemar overstates n. Resampling terms respects the grouping (Søgaard et al., EACL 2021, doi:10.18653/v1/2021.eacl-main.156; lexical memorization, Levy et al., NAACL 2015, doi:10.3115/v1/n15-1098). Row-level McNemar b/c counts stay reported as descriptive only.
- H3 (T3): macro-F1 on **unseen families** > 0.0725 (v1 holdout). Reported with bootstrap 95% CI (10k resamples, seed 7). Exploratory unless >= 8 families populated.

## Fixed design
- Test set: human-ruled gold rows with `split == test` from `slang.split.v1` (group split on `term_family`). Minimum 250 human-ruled rows covering **all test-lineage terms that have posts** (37 on 2026-10-16) (G1). The 150-term floor applies to the train pool / overall gold (G2/G3), not the test split: the hashed 10% test bucket holds only 40 terms (37 with posts), so 150 test terms is unreachable without breaking the group split. Per Danny 2026-10-16 approval of recommendation. Supporting refs: Levy et al. 2015 (doi:10.3115/v1/n15-1098), Søgaard et al. 2021 (doi:10.18653/v1/2021.eacl-main.156), Blevins & Zettlemoyer ACL 2020 (doi:10.18653/v1/2020.acl-main.95, rare-sense evaluation), Bandel et al. 2022 (arXiv:2210.12673, lexical-overlap generalization). Manifest = sorted record_ids, SHA-256 recorded here at freeze.
- Inputs: raw context + term only (no oracle slot). Reasoning off. Greedy decoding, max 8 tokens for labels.
- One training config (no sweeps): LoRA r=16, alpha=32, dropout 0.05, all linear layers, lr 2e-4 cosine, 3 epochs, seq 512, seed 7.
- Exclusions decided in advance: UNSURE and REJECT rulings excluded; rows failing G4 audit excluded from train only (never from test).
- No peeking: test labels are loaded only by `scripts/v2/prereg_eval.py --final`, run once; any rerun is reported.

## Reporting
Accuracy, macro-F1, term-level bootstrap CIs (primary), McNemar b/c counts (descriptive), per-family table, none-rate (v1 failure mode: 467/470 none). Negative results are published to the tracker as-is.

## Compute / cost estimate (ASSUMPTION-labelled)
| Step | DGX Spark / Morpheus | Paid alternative |
| --- | --- | --- |
| LoRA SFT, ~1.5k rows x 3 epochs, 8B BF16 | ~1–2 h on one Spark, $0 marginal | GPU rental ~1x H100 1 h ~ $2–4 (UNVERIFIED) |
| Inference: 4 systems x ~470 test rows | <15 min | OpenRouter BASE only (tuned LoRA cannot run there): <$0.10 |
| Term-level bootstrap | CPU, seconds | — |

Recommendation: all G5 compute on Spark/Morpheus; paid path only for BASE cross-check, with cost shown first.


## Change log
- 2026-10-16: test floor redefined (250 rows covering all test terms with posts; 150 terms moved to train pool/overall gold) and row-level McNemar replaced by term-level bootstrap. Per Danny 2026-10-16 approval of recommendation. Supersedes the 2026-10 draft wording (history kept in git).

## Freeze record (2026-10-16, per Danny go 3:55 PM PT)

- Test manifest: 273 record_ids (sorted), SHA-256 `a03c8619ba91a0f3d3edb43a358adbb5a6fcc83fe462442b6cb66e94be8296b6`. Verified unchanged after the 2026-10-16 attestation load.
- Preregistration text above (this file before this section): SHA-256 `1954a35a5bba8586489c07bf5300f28da26a20e9160e6ed693926c13613e2cbe`.
- gold_test.jsonl SHA-256 prefix `06caba1397df`. 15 quarantined gold rows (suspect synthetic source id) are excluded from test and stay quarantined.
- Tag: `v2-test-freeze-2026-10-16`. Read-only copy kept in the private tracker. Any change to the manifest after this point voids the freeze.
