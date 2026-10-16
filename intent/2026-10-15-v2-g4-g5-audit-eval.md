---
id: intent-v2-g4-g5
status: accepted (Danny, 2026-10-15 18:00 PT: "yes" to merge PR #26 and run G4/G5 on DGX Spark/Morpheus at $0 extra)
depends_on: ["007"]
---

# Intent

## Problem
Hyperlex v2 (SHADOW-only, Spec 007 A8 Nano 8B LoRA, PR #18) needs two gates before any training claim:
G4 (every SFT candidate row beats untuned BASE) and G5 (preregistered, no-peek evaluation vs BASE and baselines).

## Proposed outcome
Plans in `docs/v2/` (G4_BASE_AUDIT_PLAN.md = plan, G5_PREREG_EVAL.md = preregistration) and two scripts in `scripts/v2/`:
fail-closed BASE audit (dry run default, human gold only) and prereg evaluator (refuses test gold without `--final`,
exact McNemar + Holm). No data, post text, or sensitive terms in this repo; data stays in the operator's private store.

Out of scope: training code, Hermes skill contract, Brier/forecast, any paid compute.
