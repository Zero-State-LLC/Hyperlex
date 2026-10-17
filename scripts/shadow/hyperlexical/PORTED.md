# Ported from archived scrimshawlife-ctrl/Hyperlex @ ad4075b (2026-10-12)

Verbatim copy of the holdout guard (PR #120) and the modules its tests and the training entrypoints import (`train.py` -> `loop.run_loop` -> `admission.admit_training_run` -> `holdout_guard`). `scripts/shadow/recoverable_structure/` is the same archive commit: `export.harvest_unbind_spans` and `eval_unbind` import it, and a clean checkout was missing the package. Torch is imported lazily; the guard tests run with pytest only.
Tests: `tests/shadow/test_hyperlexical_holdout_{disjoint,guard,wiring}.py`, `tests/heldout/` (CI: `.github/workflows/holdout-guard.yml`).
