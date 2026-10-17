"""Fail-closed wiring: the training entrypoints must keep calling the holdout guard.

Static check so a refactor cannot silently drop the guard (P0, 2026-10-12)."""

from pathlib import Path

PKG = Path(__file__).resolve().parents[2] / "scripts" / "shadow" / "hyperlexical"


def test_loop_admits_and_filters_holdout():
    src = (PKG / "loop.py").read_text(encoding="utf-8")
    assert "admit_training_run(" in src
    assert "filter_holdout_rows(train, spec)" in src
    assert "assert_no_holdout(" in src


def test_admission_requires_holdout():
    assert "require_holdout_for_training()" in (PKG / "admission.py").read_text(encoding="utf-8")


def test_train_entrypoint_runs_through_loop():
    src = (PKG / "train.py").read_text(encoding="utf-8")
    assert "merge_manifest_env" in src and "run_loop(" in src


def test_no_new_trainer_bypasses_the_guard():
    allowed = {"train.py", "train_input.py", "training_routing.py", "training_schedule.py"}
    for path in PKG.glob("train*.py"):
        assert path.name in allowed, f"new training entrypoint {path.name}: route it through loop.run_loop/admission"
