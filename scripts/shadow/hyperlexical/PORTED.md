# Ported from archived scrimshawlife-ctrl/Hyperlex @ ad4075b (2026-10-12)

Verbatim copy of the holdout guard (PR #120) and the 57 modules its tests and the training entrypoints import (`train.py` -> `loop.run_loop` -> `admission.admit_training_run` -> `holdout_guard`). No logic changes. Torch is imported lazily; the guard tests run with pytest only.
Tests: `tests/shadow/test_hyperlexical_holdout_{disjoint,guard,wiring}.py`, `tests/heldout/` (CI: `.github/workflows/holdout-guard.yml`).
