import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "shadow"))

from hyperlexical import run_report as rr


def test_noop_when_env_unset(tmp_path, monkeypatch):
    monkeypatch.delenv(rr.ENV, raising=False)
    with rr.RunReport("tool", {}, path=None):
        pass
    assert list(tmp_path.iterdir()) == []


def test_writes_with_env(tmp_path, monkeypatch):
    path = tmp_path / "sub" / "report.json"
    monkeypatch.setenv(rr.ENV, str(path))
    with rr.RunReport("mytool", {"a": 1}, path=None) as r:
        r.set_counts(rows=10)
        r.set_scores(score=0.9)
        r.set_validity(8, 2)
        r.warn("hello")
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["schema"] == "run_report.v1"
    assert data["tool"] == "mytool"
    assert data["inputs"] == {"a": 1}
    assert data["counts"] == {"rows": 10}
    assert data["scores"] == {"score": 0.9}
    assert data["validity"] == {"valid": 8, "invalid": 2, "valid_rate": 0.8}
    assert data["warnings"] == ["hello"]
    assert data["status"] == "ok"
    assert "started_at" in data and "finished_at" in data and "duration_ms" in data
    assert data["errors"] == []


def test_error_status_and_exception_propagates(tmp_path, monkeypatch):
    path = tmp_path / "report.json"
    monkeypatch.setenv(rr.ENV, str(path))
    with pytest.raises(ValueError):
        with rr.RunReport("tool", {}, path=None):
            raise ValueError("boom")
    data = json.loads(path.read_text())
    assert data["status"] == "error"
    assert data["errors"] == ["ValueError: boom"]


def test_explicit_status(tmp_path, monkeypatch):
    path = tmp_path / "report.json"
    monkeypatch.setenv(rr.ENV, str(path))
    with rr.RunReport("tool", {}, path=None) as r:
        r.set_status("skipped")
    data = json.loads(path.read_text())
    assert data["status"] == "skipped"


def test_validity_rate_math_and_none_when_zero(tmp_path, monkeypatch):
    path = tmp_path / "report.json"
    monkeypatch.setenv(rr.ENV, str(path))
    with rr.RunReport("tool", {}, path=None) as r:
        r.set_validity(3, 1)
    data = json.loads(path.read_text())
    assert data["validity"]["valid_rate"] == 0.75

    with rr.RunReport("tool2", {}, path=None) as r2:
        r2.set_validity(0, 0)
    data2 = json.loads(path.read_text())
    assert data2["validity"]["valid_rate"] is None


def test_write_failure_does_not_raise(tmp_path, monkeypatch, capsys):
    path = tmp_path / "dir"
    path.mkdir()
    monkeypatch.setenv(rr.ENV, str(path))
    with rr.RunReport("tool", {}, path=None):
        pass
    captured = capsys.readouterr()
    assert "Failed to write" in captured.err


def test_safe_inputs():
    d = {
        "text": "secret",
        "rows": [1, 2, 3],
        "list50": list(range(50)),
        "list51": list(range(51)),
        "other": "ok",
    }
    safe = rr.safe_inputs(d)
    assert "text" not in safe
    assert "rows" not in safe
    assert safe["list50"] == list(range(50))
    assert safe["list51"] == "<list len=51>"
    assert safe["other"] == "ok"
