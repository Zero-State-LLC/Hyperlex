"""Private registry overlay: sensitive family members load from a local file, never the repo."""

from __future__ import annotations

import copy
import json

from hyperlex.analysis import LINEAGE_REGISTRY, _load_private_registry_overlay, match_lineage


def test_public_registry_has_no_betting_sharp_and_new_families():
    ids = {e["family_id"] for e in LINEAGE_REGISTRY}
    assert "betting-sharp" not in ids
    assert {"imageboard-meta", "discourse-accusation", "status-labels",
            "tiktok-lifestyle", "weeb-otaku", "neuro-insult"} <= ids
    terms = {t for e in LINEAGE_REGISTRY for t in e["terms"]}
    assert "parlay" not in terms


def test_overlay_extends_and_appends(tmp_path, monkeypatch):
    ov = tmp_path / "overlay.json"
    ov.write_text(json.dumps({"families": [
        {"family_id": "neuro-insult", "terms": ["zzplaceholdera", "zzplaceholderb"]},
        {"family_id": "zz-new", "terms": ["zzplaceholderc"]},
    ]}))
    reg = copy.deepcopy(LINEAGE_REGISTRY)
    monkeypatch.setenv("HYPERLEX_PRIVATE_REGISTRY", str(ov))
    assert _load_private_registry_overlay(reg) == str(ov)
    by = {e["family_id"]: e for e in reg}
    assert by["neuro-insult"]["terms"][-2:] == ["zzplaceholdera", "zzplaceholderb"]
    assert by["zz-new"]["terms"] == ["zzplaceholderc"]
    hit = match_lineage("zzplaceholdera zzplaceholderb", registry=reg, use_vector=False)
    assert hit and hit["family_id"] == "neuro-insult"


def test_overlay_missing_is_noop(tmp_path, monkeypatch):
    monkeypatch.setenv("HYPERLEX_PRIVATE_REGISTRY", str(tmp_path / "nope.json"))
    reg = copy.deepcopy(LINEAGE_REGISTRY)
    assert _load_private_registry_overlay(reg) is None
    assert reg == LINEAGE_REGISTRY


def test_overlay_bad_root_is_noop(tmp_path, monkeypatch):
    ov = tmp_path / "overlay.json"
    ov.write_text("[]")
    monkeypatch.setenv("HYPERLEX_PRIVATE_REGISTRY", str(ov))
    reg = copy.deepcopy(LINEAGE_REGISTRY)
    assert _load_private_registry_overlay(reg) is None
    assert reg == LINEAGE_REGISTRY


def test_public_registry_excludes_overlay_terms():
    from hyperlex.analysis import PUBLIC_LINEAGE_REGISTRY

    terms = {t for e in PUBLIC_LINEAGE_REGISTRY for t in e.get("terms") or []}
    assert "zzplaceholdera" not in terms


def test_ambiguous_beta_needs_context():
    assert not (match_lineage("we ship the beta release tomorrow", use_vector=False) or {}).get("family_id")


def test_ambiguous_beta_with_family_cue_still_matches():
    hit = match_lineage("typical beta normie take", use_vector=False)
    assert hit and hit["family_id"] == "status-labels"
