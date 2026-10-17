---
id: 007/amendments
status: see specs/index.yaml
depends_on: ["007"]
dag: specs/DAG.md
---

# Amendments 007

## A1 — C6 ceiling 150M
T1 ≤ 150M.

## A2 — freeze trunk ModernBERT-base
`answerdotai/ModernBERT-base`.

## A3 — U3 specify lock
C33–C40.

## A4 — keepable train layout (2026-09-09)
C41–C46. Freeze last-2. Classify + token-state unbind heads. Values still from Spark.

## A5 — milestones + engineering guidelines (2026-09-10)
Notion-first, then disk.
- `milestones.md` — name-gate 2k/200/200, T0/T1/T2 pointer, R2 exit. Does not fork locked spec tiers.
- `engineering.md` — classify / files / merge / Spark-later rules.
- Notion: https://app.notion.com/p/3d73e8ba2f5c81e9aac1e7dc992e3481 · https://app.notion.com/p/3d73e8ba2f5c813db326e3f68ac77ee9
Does not train. Does not set `name_gate`. Does not open 006 or 008.

## A6 — `name_gate` yes for `seed-morph78` (2026-09-24)
Danny: **`flip name_gate`**. Receipt: `receipts/20260924-name-gate-yes-morph78.md`.
- Sets product-level `name_gate=true` for pin `seed-morph78` only. That pin may be called **Hyperlexical**.
- Basis: T1 tier (`milestones.md`) — ModernBERT-base trunk (A2, ≤150M per A1), unbind heads, trained E2 PASS vs Spec 004 probe; dataset buckets 0/0/0; soft_ceiling PROMOTE_BEST.
- Amends `engineering.md` merge rule: a PR may set `name_gate` true only when it records a Danny yes as an amendment (this one).
- Does not rename card/package identifiers (`hyperlex-encoder-*`; C31 target `hyperlex-structure-149m`), does not change SHADOW packet/schema `name_gate` fields, does not authorize Hub upload or T13, does not start a climb.

## A8: Hyperlex v2 base model, Nemotron Nano 8B (2026-10-10)
Danny approved on 2026-10-10 at 20:40 PT. This amends Spec 007 non-goals N1 ("Chat model, 7B+ general LM, or Hyperlex GPT") and N11 ("Using a safety-tuned instruct checkpoint as the T1 product trunk"), as written in `spec.md` of the archived repo scrimshawlife-ctrl/Hyperlex (this repo did not carry `spec.md` over). Numbered A8 because A7 (A1 ceiling counts trunk parameters, 2026-09-24) also lives only in the archived repo. The amendment applies to one separate artifact, **Hyperlex v2**. It does not change T1.

**What it allows**
- Hyperlex v2 is a LoRA/SFT on `nvidia/Llama-3.1-Nemotron-Nano-8B-v1`. Model card (checked 2026-10-10): 8,030,261,248 parameters, BF16, context up to 131,072 tokens, built from Llama 3.1 8B Instruct, governed by the NVIDIA Open Model License with the Llama 3.1 Community License as additional terms ("Built with Llama").
- Tasks are restricted to T1 sense classification (`SLANG_SENSE` / `OTHER_SENSE` per observation) and T2 contextual meaning. T3 lineage comes only after the classify label-admission filter (rc3 DISTILL). Mutation trace stays rule/detector. Forecasting stays out.

**What stays locked**
- N2/N3: `brier` stays null, `forecast_eligible: false`, routes form|lexical only. The model emits no forecasts.
- The name **Hyperlexical**, `name_gate`, and the A1/A2 T1 trunk (ModernBERT, 150M trunk ceiling) are unchanged. Hyperlex v2 is not T1, not a chat product, and not "Hyperlex GPT".
- Hub stays closed. Weights and the dataset stay private (vernacular-ingest D15). Nothing is published.
- VII dual-use and N4/N12 still apply.

**Why**
1. Sense and meaning in context are generative and contextual. An encoder classify head on bare atoms reached reserve macro-F1 0.0725 on unseen slang. The failures traced to leaks (per-row splits, closed-vocab OOV counted as hits, gold-span eval) and to rule-derived labels, not to trunk size alone. An instruct 8B base can read the full post and produce a meaning, which T1 cannot.
2. Nano 8B fits a single GPU and the DGX Spark, with LoRA as NVIDIA's recommended path for small domain sets. That keeps training and inference local and offline-capable.
3. The N11 worry (refusing or rewriting dialect) is tested, not assumed. E6 no-refusal on civilian slang is a hard gate for v2, and BASE refusals are measured first.

**Gates before any v2 claim**
- The Hyperlex v2 dataset gates (vernacular-ingest `workspace.slang_dev`, Obsidian "Hyperlex v2 dataset tracker") pass: human-ruled gold eval of at least 250 rows, whole `term_family` groups (`slang.split.v1`), with the manifest hashed before training.
- Every SFT row must beat untuned Nano 8B (BASE) output (the Athanor r8 audit-as-you-go lesson), with dedup and rights checked.
- Pre-registered eval: beat BASE, a bag-of-terms LR, and the registry rule with exact McNemar p<.05 on identical rows. Report macro-F1 on unseen families against 0.0725.

This amendment does not train anything, does not set `name_gate`, and does not open the Hub.

