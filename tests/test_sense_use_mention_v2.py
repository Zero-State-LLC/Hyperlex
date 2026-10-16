"""Spec 009 T028: the Jev sense labeller emits use_mention under rebuilt-sense-v2."""
import json, os, sqlite3, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "v2"))
import sense_labels as sl

V2 = json.load(open(os.path.join(os.path.dirname(__file__), "..", "specs", "009-ruling-label-taxonomy", "contracts", "jev_sense_contract.v2.json")))
V1 = {k: v for k, v in V2.items() if k not in ("closed_set_use_mention",)}
V1["version"] = "rebuilt-sense-v1"


def _a(choice, p):
    return {"choice": choice, "probabilities": {choice: p}}


def test_v2_request_has_use_mention_question_per_post():
    req = sl.build_request("zorbly", {}, [("o1", "t1"), ("o2", "t2")], V2)
    assert set(req["questions"]) == {"p0", "p1", "p0_um", "p1_um"}
    assert set(req["questions"]["p0_um"]["criteria"]) == {"USE", "MENTION"}


def test_v1_request_unchanged():
    req = sl.build_request("zorbly", {}, [("o1", "t1")], V1)
    assert set(req["questions"]) == {"p0"}


def test_parse_use():
    assert sl.parse_answer({"p0": _a("SLANG_SENSE", 0.9), "p0_um": _a("USE", 0.8)}, "p0", V2) == ("SLANG_SENSE", 0.9, "USE")


def test_mention_is_never_slang_sense():
    lab, _, um = sl.parse_answer({"p0": _a("SLANG_SENSE", 0.9), "p0_um": _a("MENTION", 0.9)}, "p0", V2)
    assert (lab, um) == ("OTHER_SENSE", "MENTION")


def test_missing_or_low_use_mention_fails_closed_to_none():
    assert sl.parse_answer({"p0": _a("OTHER_SENSE", 0.9)}, "p0", V2)[2] is None
    assert sl.parse_answer({"p0": _a("OTHER_SENSE", 0.9), "p0_um": _a("MENTION", 0.2)}, "p0", V2)[2] is None
    assert sl.parse_answer({"p0": _a("OTHER_SENSE", 0.9), "p0_um": _a("BOTH", 0.9)}, "p0", V2)[2] is None


def test_v1_parse_has_no_use_mention():
    assert sl.parse_answer({"p0": _a("SLANG_SENSE", 0.9), "p0_um": _a("MENTION", 0.9)}, "p0", V1) == ("SLANG_SENSE", 0.9, None)


def test_low_sense_prob_is_unknown():
    assert sl.parse_answer({"p0": _a("SLANG_SENSE", 0.3)}, "p0", V2)[0] == "UNKNOWN"


def test_ensure_table_adds_column_additively():
    db = os.path.join(tempfile.mkdtemp(), "v.sqlite3")
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE observation_sense_v1 (observation_id TEXT PRIMARY KEY, term_id TEXT NOT NULL, label TEXT NOT NULL, "
                "prob REAL, contract_version TEXT NOT NULL, computed_at TEXT NOT NULL)")
    con.execute("INSERT INTO observation_sense_v1 VALUES ('o1','t','SLANG_SENSE',1.0,'rebuilt-sense-v1','x')")
    sl.ensure_table(con); sl.ensure_table(con)
    assert con.execute("SELECT label, use_mention FROM observation_sense_v1").fetchall() == [("SLANG_SENSE", None)]
