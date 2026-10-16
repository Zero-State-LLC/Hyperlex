# Hyperlex v2 — G4 BASE audit plan (draft)

Status: DRAFT for Danny's review. SHADOW-only artifact. Not Hyperlexical T1 (see Spec 007 A8, PR #18).
Data: private local store (`slang_v1.sqlite3` / `curated_sense_observation.jsonl`) on the box. **No post text and
no slur-tagged terms are committed to this repo**; scripts read IDs + private paths at run time only.

## Goal (gate G4)
Run the untuned base model (`nvidia/Llama-3.1-Nemotron-Nano-8B-v1`, reasoning off) on every candidate SFT row.
Keep a row only if its curated target beats BASE (r8 audit-as-you-go rule; Athanor lesson: SFT targets lost to BASE on 68% of rows).

## Procedure
1. Inputs per row: raw context + term only (no gold span / oracle slot). Prompt fixed in `scripts/v2/base_audit.py` (hash recorded).
2. T1: BASE predicts `SLANG_SENSE | OTHER_SENSE`. Row is *informative* if BASE is wrong vs human/OBSERVED label; rows where BASE is
   already right are kept at a capped share (default 30%) so the set is not adversarial-only.
3. T2: BASE writes a short meaning; a pairwise judge (blind A/B, order randomized, seed fixed) compares BASE vs curated target.
   Keep only `target_wins`. Ties/`base_wins` -> drop with reason code.
4. Hygiene in the same pass: exact + near-dup (content_sha256, MinHash 0.8) across splits; rights must be `allowed_internal`;
   model-generated share <= 20% (Shumailov 2024); grouped split by `term_family` unchanged.
5. Output: `audit_v1.jsonl` (record_id, base_label, base_correct, judge_verdict, keep, reason) — private; summary counts only to tracker.

## Exit criteria
- 100% of candidate rows audited; per-row verdict stored; keep-rate reported per split and per lineage family.
- Judge agreement check: 50 rows double-judged (swap order) — agreement >= 85% or judge is replaced.

## Compute / cost estimate (ASSUMPTION-labelled)
Rows: ~1,100 curated now (up to ~1,360 if 4chan rows are promoted). Tokens ~ 400 in + 120 out per row (BASE) and ~700 in + 50 out (judge).

| Option | BASE pass | Judge pass | Wall time | Cost |
| --- | --- | --- | --- | --- |
| DGX Spark (vLLM, BF16, batch 32) | T1 ~0.08M tok (measured dry-run, 1,091 rows); T2 ~0.5M | local 8B-70B judge | ~0.5–1.5 h | $0 marginal (power only) |
| Morpheus (same, if free GPU) | same | same | ~same | $0 marginal |
| OpenRouter BASE (Nemotron-class 8B) + cheap judge (deepseek-v4.1-flash) | ~0.6M tok | ~1.0M tok | <20 min | ~$0.10–$1.00 total (prices UNVERIFIED; confirm on openrouter.ai before spend) |

Recommendation: BASE on Spark (exact base weights, reproducible); judge on Spark if a >=70B judge fits, otherwise OpenRouter judge
with cost shown and approved first. Nothing runs without Danny's yes.
