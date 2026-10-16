# Hyperlex v2 — G5 preregistered evaluation (draft)

Status: DRAFT preregistration. Freeze (hash this file + test manifest) **before** any training run. SHADOW-only.

## Hypotheses
- H1 (T1): LoRA-tuned Nano 8B beats BASE on T1 sense accuracy on the hashed grouped test split. Exact McNemar, two-sided, alpha=0.05.
- H2 (T1): LoRA beats bag-of-terms (logistic regression on term+context unigrams) and the rule baseline (`observation_sense_v1`). Exact McNemar each, Holm correction across the 3 comparisons.
- H3 (T3): macro-F1 on **unseen families** > 0.0725 (v1 holdout). Reported with bootstrap 95% CI (10k resamples, seed 7). Exploratory unless >= 8 families populated.

## Fixed design
- Test set: human-ruled gold rows with `split == test` from `slang.split.v1` (group split on `term_family`). Minimum 250 rows / 150 terms (G1). Manifest = sorted record_ids, SHA-256 recorded here at freeze.
- Inputs: raw context + term only (no oracle slot). Reasoning off. Greedy decoding, max 8 tokens for labels.
- One training config (no sweeps): LoRA r=16, alpha=32, dropout 0.05, all linear layers, lr 2e-4 cosine, 3 epochs, seq 512, seed 7.
- Exclusions decided in advance: UNSURE and REJECT rulings excluded; rows failing G4 audit excluded from train only (never from test).
- No peeking: test labels are loaded only by `scripts/v2/prereg_eval.py --final`, run once; any rerun is reported.

## Reporting
Accuracy, macro-F1, McNemar b/c counts and exact p, per-family table, none-rate (v1 failure mode: 467/470 none). Negative results are published to the tracker as-is.

## Compute / cost estimate (ASSUMPTION-labelled)
| Step | DGX Spark / Morpheus | Paid alternative |
| --- | --- | --- |
| LoRA SFT, ~1.5k rows x 3 epochs, 8B BF16 | ~1–2 h on one Spark, $0 marginal | GPU rental ~1x H100 1 h ~ $2–4 (UNVERIFIED) |
| Inference: 4 systems x ~470 test rows | <15 min | OpenRouter BASE only (tuned LoRA cannot run there): <$0.10 |
| Bootstrap/McNemar | CPU, seconds | — |

Recommendation: all G5 compute on Spark/Morpheus; paid path only for BASE cross-check, with cost shown first.
