"""G5 prereg_eval --final guards: manifest sha, threshold-config sha, run-once lock, manifest coverage, threshold."""
import hashlib, json, os, subprocess, sys, tempfile
import pytest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "v2", "prereg_eval.py")


def _sha(b):
    return hashlib.sha256(b).hexdigest()


@pytest.fixture
def env(tmp_path):
    man = b"a\nb\nc\n"; cfg = json.dumps({"threshold": 0.5}).encode(); pre = b"prereg final\n"
    (tmp_path / "m.txt").write_bytes(man); (tmp_path / "t.json").write_bytes(cfg); (tmp_path / "pre.md").write_bytes(pre)
    (tmp_path / "spent.txt").write_bytes(b"x\n")
    gold = [{"record_id": "a", "gold": "SLANG_SENSE", "family": "x", "stratum": "U"}, {"record_id": "b", "gold": "OTHER_SENSE", "family": "y", "stratum": "S"},
            {"record_id": "c", "gold": "OTHER_SENSE", "family": "y", "stratum": "U"}, {"record_id": "z", "gold": "SLANG_SENSE", "family": "q"}]
    (tmp_path / "g.jsonl").write_text("".join(json.dumps(r) + "\n" for r in gold))
    src = open(SCRIPT).read()
    src = src.replace(src.split("MANIFEST_SHA = ")[1].split("\n")[0], json.dumps(_sha(man)), 1)
    src = src.replace(src.split("THRESHOLD_CFG_SHA = ")[1].split("\n")[0], json.dumps(_sha(cfg)), 1)
    src = src.replace(src.split("PREREG_SHA = ")[1].split("\n")[0], json.dumps(_sha(pre)), 1)
    src = src.replace(src.split("SPENT_MANIFESTS = ")[1].split("\n")[0], json.dumps({_sha(b"x\n"): "spent fixture"}), 1)
    (tmp_path / "pe.py").write_text(src)
    return tmp_path


def _preds(d, rows, name="p.jsonl"):
    (d / name).write_text("".join(json.dumps(r) + "\n" for r in rows)); return str(d / name)


def _run(d, preds, *extra, lock="L", script="pe.py", full=True, manifest="m.txt"):
    args = [sys.executable, str(d / script), "--gold", str(d / "g.jsonl"), "--tuned", preds, "--final"]
    if full:
        args += ["--manifest", str(d / manifest), "--threshold-config", str(d / "t.json"), "--lock", str(d / lock), "--prereg", str(d / "pre.md")]
    return subprocess.run(args + list(extra), capture_output=True, text=True)


MARGINS = [{"record_id": "a", "margin": 2.0}, {"record_id": "b", "margin": 0.2}, {"record_id": "c", "margin": 0.9}]


def test_requires_final():
    r = subprocess.run([sys.executable, SCRIPT, "--gold", "g", "--tuned", "t"], capture_output=True, text=True)
    assert r.returncode != 0 and "--final" in r.stderr


def test_final_requires_guards(env):
    r = _run(env, _preds(env, MARGINS), full=False)
    assert r.returncode != 0 and "requires --manifest" in r.stderr


def test_applies_locked_threshold_and_scores_manifest_only(env):
    r = _run(env, _preds(env, MARGINS))
    assert r.returncode == 0, r.stderr
    rep = json.loads(r.stdout)
    assert rep["n"] == 3 and rep["threshold"] == 0.5
    assert abs(rep["tuned_acc"] - 2 / 3) < 1e-9  # a=S ok, b=O ok, c=S (0.9>0.5) wrong
    assert rep["per_label"]["OTHER_SENSE"]["recall"] == 0.5 and rep["confusion_gold_x_pred"]["OTHER_SENSE"]["SLANG_SENSE"] == 1
    assert rep["by_stratum"]["U"]["n"] == 2 and rep["by_stratum"]["S"]["acc"] == 1.0


def test_second_final_run_refuses(env):
    p = _preds(env, MARGINS)
    assert _run(env, p).returncode == 0
    r = _run(env, p)
    assert r.returncode != 0 and "refusing second --final run" in r.stderr


def test_manifest_sha_mismatch_refuses(env):
    (env / "m.txt").write_text("a\nb\n")
    r = _run(env, _preds(env, MARGINS))
    assert r.returncode != 0 and "manifest sha mismatch" in r.stderr


def test_threshold_config_sha_mismatch_refuses(env):
    (env / "t.json").write_text(json.dumps({"threshold": 0.0}))
    r = _run(env, _preds(env, MARGINS))
    assert r.returncode != 0 and "threshold config sha mismatch" in r.stderr


def test_pred_disagreeing_with_threshold_refuses(env):
    rows = [dict(MARGINS[0], pred="OTHER_SENSE")] + MARGINS[1:]
    r = _run(env, _preds(env, rows))
    assert r.returncode != 0 and "disagrees with locked threshold" in r.stderr


def test_missing_manifest_prediction_refuses(env):
    r = _run(env, _preds(env, MARGINS[:2]))
    assert r.returncode != 0 and "cover the frozen manifest" in r.stderr


def test_spent_manifest_refuses(env):
    r = _run(env, _preds(env, MARGINS), manifest="spent.txt")
    assert r.returncode != 0 and "manifest is spent" in r.stderr
    assert not (env / "L").exists()


def test_prereg_sha_mismatch_refuses(env):
    (env / "pre.md").write_text("edited")
    r = _run(env, _preds(env, MARGINS))
    assert r.returncode != 0 and "prereg sha mismatch" in r.stderr


def test_failed_checks_do_not_burn_the_lock(env):
    r = _run(env, _preds(env, MARGINS[:2]))
    assert r.returncode != 0 and not (env / "L").exists()
    assert _run(env, _preds(env, MARGINS)).returncode == 0
