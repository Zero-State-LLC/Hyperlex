"""The training export must import recoverable_structure in a clean checkout."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_training_export_imports_bundled_recoverable_structure(tmp_path: Path) -> None:
    shadow = ROOT / "scripts" / "shadow"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(shadow)
    env.pop("HLX_E2_DISJOINT", None)
    code = """
from hyperlexical.export import harvest_unbind_spans
from recoverable_structure.fit import _split, fit_scheme, run_probe, swap_accuracy
from recoverable_structure.fixtures import make_spans, snapshot

rows = harvest_unbind_spans(4)
assert len(rows) == 4 and rows[0][1]["item_ids"]
spans = make_spans(n=8, length=4, seed=7)
train, test, digest = _split(len(spans), seed=7)
assert train and test and len(digest) == 16
snap = snapshot("atomic_pair", n=4, length=4, dim=4, seed=7)
assert len(snap["encodings"]) == 4
assert callable(fit_scheme) and callable(run_probe) and callable(swap_accuracy)
"""
    proc = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
