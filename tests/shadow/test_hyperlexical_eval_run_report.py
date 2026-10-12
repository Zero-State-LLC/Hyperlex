"""run_report.v1 wiring for eval_classify (report-only; P3/P4, 2026-10-12)."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "shadow"))

from hyperlexical import eval_classify  # noqa: E402


def _w(path, rows):
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


def _fixture(tmp_path, bad_pred=False):
    fams = ["ai-native", "gaming-meta", "none"]
    ev = [{"id": f"e{i}", "text": f"eval {i} {fams[i % 3]}", "lineage": fams[i % 3]} for i in range(9)]
    tr = [{"id": f"t{i}", "text": f"train {i} {fams[i % 3]}", "lineage": fams[i % 3]} for i in range(30)]
    pr = [{"id": r["id"], "pred": r["lineage"]} for r in ev]
    if bad_pred:
        pr[0]["pred"] = "not-a-family"
    _w(tmp_path / "eval.jsonl", ev)
    _w(tmp_path / "train.jsonl", tr)
    _w(tmp_path / "preds.jsonl", pr)
    return ["--preds", str(tmp_path / "preds.jsonl"), "--eval", str(tmp_path / "eval.jsonl"), "--train", str(tmp_path / "train.jsonl")]


def test_no_env_no_report_same_stdout(tmp_path, monkeypatch, capsys):
    argv = _fixture(tmp_path)
    monkeypatch.delenv("HLX_RUN_REPORT", raising=False)
    assert eval_classify.main(argv) == 0
    first = capsys.readouterr().out
    monkeypatch.setenv("HLX_RUN_REPORT", str(tmp_path / "rr.json"))
    assert eval_classify.main(argv) == 0
    assert capsys.readouterr().out == first
    rep = json.loads((tmp_path / "rr.json").read_text())
    assert rep["schema"] == "run_report.v1" and rep["status"] == "ok"
    assert rep["validity"]["valid_rate"] == 1.0


def test_invalid_label_counted_separately(tmp_path, monkeypatch, capsys):
    argv = _fixture(tmp_path, bad_pred=True)
    monkeypatch.setenv("HLX_RUN_REPORT", str(tmp_path / "rr.json"))
    eval_classify.main(argv)
    capsys.readouterr()
    rep = json.loads((tmp_path / "rr.json").read_text())
    assert rep["validity"]["invalid"] == 1 and rep["validity"]["valid"] == 8
    assert "text" not in json.dumps(rep["inputs"])
