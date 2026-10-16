"""Spec 009 T026: export context is the target-centred window; R row statuses are never gold."""
import json, os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "v2"))
import export_splits as ex
import ruling_queue as rq


def _row(rid, term, text, split="test", sense="SLANG_SENSE", **h):
    hr = {"source": "human", "sense": sense, "split": split, **h}
    return {"record_id": rid, "term": term, "term_family": "fam-a", "contextual_use": text,
            "content_sha256": rid, "sense_candidate": "SLANG_SENSE", "human_ruling": hr,
            "mutation_lineage": {"lineage_family": "general-slang"}, "model_proposal": {}, "sensitivity": {}}


def _run(rows):
    d = tempfile.mkdtemp()
    src = os.path.join(d, "in.jsonl")
    with open(src, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    ex.main(src=src, out=d)
    out = {}
    for s in ("train", "val", "test"):
        out.update({x["record_id"]: x for x in map(json.loads, open(os.path.join(d, s + ".jsonl")))})
    return out, json.load(open(os.path.join(d, "export_report.json"))), d


def test_context_is_target_window_not_head():
    text = "x" * 2000 + " zorbly " + "y" * 2000
    out, _, _ = _run([_row("r1", "zorbly", text)])
    ctx = out["r1"]["context"]
    assert "zorbly" in ctx and len(ctx) <= rq.EXCERPT_CHARS + 2
    assert out["r1"]["context_match"] == "word"


def test_short_text_unchanged():
    out, _, _ = _run([_row("r1", "zorbly", "so zorbly")])
    assert out["r1"]["context"] == "so zorbly"


def test_non_gold_row_status_excluded():
    rows = [_row("ta", "zorbly", "a zorbly", row_status="TARGET_ABSENT"),
            _row("ue", "zorbly", "b zorbly", row_status="UNUSABLE_EVIDENCE"),
            _row("ok", "zorbly", "c zorbly", use_mention="USE")]
    out, rep, d = _run(rows)
    gold = {json.loads(l)["record_id"] for l in open(os.path.join(d, "gold_test.jsonl"))}
    assert gold == {"ok"}
    assert out["ta"]["label_source"].startswith("model:") and out["ta"]["row_status"] == "TARGET_ABSENT"
    assert out["ok"]["use_mention"] == "USE"
    assert rep["non_gold_row_status_rows"] == 2


def test_gold_helper_matches_ruling_queue():
    for st in rq.NON_GOLD_ROW_STATUS:
        assert ex.gold({"human_ruling": {"source": "human", "sense": "OTHER_SENSE", "row_status": st}}) is None
    assert ex.gold({"human_ruling": {"source": "human", "sense": "OTHER_SENSE"}}) == "OTHER_SENSE"
