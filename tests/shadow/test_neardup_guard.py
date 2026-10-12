import json
import pytest
from scripts.shadow.hyperlexical import neardup_guard as g

TRAIN = [{"text": "the vibe was totally mid tonight fr"}, {"text": "completely unrelated sentence about cats"}]
VAL = [{"text": "The vibe was totally MID tonight, fr!"}]


def test_jaccard_basics():
    a = g.char_ngrams("hello world")
    assert g.jaccard(a, a) == 1.0
    assert g.jaccard(a, frozenset()) == 0.0


def test_find_exact_normalized_dup():
    pairs = g.find_near_duplicates([r["text"] for r in TRAIN], [r["text"] for r in VAL], 0.7)
    assert pairs == [{"train_index": 0, "other_index": 0, "jaccard": 1.0}]


def test_threshold_configurable():
    t, o = ["the vibe was totally mid tonight"], ["the vibe was kinda mid tonight"]
    j = g.find_near_duplicates(t, o, 0.01)[0]["jaccard"]
    assert 0 < j < 1
    assert g.find_near_duplicates(t, o, min(1.0, j + 0.01)) == []


def test_noop_by_default(monkeypatch):
    monkeypatch.delenv("HLX_NEARDUP_GUARD", raising=False)
    out, receipt = g.enforce_from_env({"a": TRAIN}, {"a": VAL})
    assert receipt is None and out["a"] == TRAIN


def _holdout(tmp_path, texts):
    p = tmp_path / "h.jsonl"
    p.write_text("\n".join(json.dumps({"text": t}) for t in texts))
    return str(p)


def test_fail_closed_on_val_dup(monkeypatch, tmp_path):
    monkeypatch.setenv("HLX_NEARDUP_GUARD", "1")
    monkeypatch.setenv("HLX_NEARDUP_HOLDOUT_TEXTS", _holdout(tmp_path, ["nothing alike here at all"]))
    with pytest.raises(SystemExit, match="ADMISSION FAIL"):
        g.enforce_from_env({"a": TRAIN}, {"a": VAL})


def test_fail_closed_on_holdout_dup(monkeypatch, tmp_path):
    monkeypatch.setenv("HLX_NEARDUP_GUARD", "1")
    monkeypatch.setenv("HLX_NEARDUP_HOLDOUT_TEXTS", _holdout(tmp_path, ["Completely unrelated sentence about cats."]))
    with pytest.raises(SystemExit, match="train_vs_holdout=1"):
        g.enforce_from_env({"a": TRAIN}, {"a": []})


def test_enabled_requires_holdout_path(monkeypatch):
    monkeypatch.setenv("HLX_NEARDUP_GUARD", "1")
    monkeypatch.delenv("HLX_NEARDUP_HOLDOUT_TEXTS", raising=False)
    with pytest.raises(SystemExit, match="REFUSE"):
        g.enforce_from_env({"a": TRAIN}, {"a": VAL})


def test_bad_threshold_refused(monkeypatch, tmp_path):
    monkeypatch.setenv("HLX_NEARDUP_GUARD", "1")
    monkeypatch.setenv("HLX_NEARDUP_THRESHOLD", "1.5")
    with pytest.raises(SystemExit, match="REFUSE"):
        g.config_from_env()


def test_drop_mode_removes_rows(monkeypatch, tmp_path):
    monkeypatch.setenv("HLX_NEARDUP_GUARD", "1")
    monkeypatch.setenv("HLX_NEARDUP_MODE", "drop")
    monkeypatch.setenv("HLX_NEARDUP_HOLDOUT_TEXTS", _holdout(tmp_path, ["nothing alike here at all"]))
    out, receipt = g.enforce_from_env({"a": TRAIN}, {"a": VAL})
    assert out["a"] == TRAIN[1:] and receipt["per_set"]["a"]["train_rows_dropped"] == 1


def test_scales(monkeypatch):
    import random
    rnd = random.Random(0)
    words = [f"w{i}" for i in range(500)]
    train = [" ".join(rnd.choices(words, k=12)) for _ in range(3000)]
    other = [" ".join(rnd.choices(words, k=12)) for _ in range(300)] + [train[5]]
    pairs = g.find_near_duplicates(train, other, 0.7)
    assert {"train_index": 5, "other_index": 300, "jaccard": 1.0} in pairs
