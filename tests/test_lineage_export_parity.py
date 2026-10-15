"""Parity with the archived scrimshawlife-ctrl/Hyperlex main (ad4075b9) for the vernacular export.

Expected families are match_lineage(term, use_vector=False) outputs on the archive for the 336-term
vernacular export (2026-10-15 PT). Lexical only; no network, no vector DB.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from hyperlex.analysis import match_lineage

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_FAMILY = {
    "67": "brainrot-aura",
    "aura": "brainrot-aura",
    "aura farming": "brainrot-aura",
    "canon event": "brainrot-aura",
    "cooked": "brainrot-aura",
    "copium": "political-status",
    "cracked": "gaming-meta",
    "degen": "crypto-degen",
    "glaze": "ai-native",
    "gooner": "brainrot-aura",
    "gooning": "brainrot-aura",
    "lowkenuinely": "brainrot-aura",
    "lowkey": "brainrot-aura",
    "main character energy": "brainrot-aura",
    "memecoin": "crypto-degen",
    "mid": "brainrot-aura",
    "mog": "brainrot-aura",
    "mogged": "brainrot-aura",
    "mogging": "brainrot-aura",
    "ngmi": "crypto-degen",
    "return to office": "workplace-corp",
    "rizz": "brainrot-aura",
    "seethe": "political-status",
    "sigma": "brainrot-aura",
    "skibidi": "brainrot-aura",
    "slay": "brainrot-aura",
    "slop": "ai-native",
    "slop grenade": "ai-native",
    "touch grass": "gaming-meta",
    "unc": "kinship-address",
    "wagmi": "crypto-degen"
}

EXPECTED_NONE = [
    "____ edit",
    "aired",
    "al bundy effect",
    "algo",
    "amish bus driver rule",
    "anchovy",
    "anons",
    "art",
    "artstyle",
    "assmosis",
    "atomic blonde",
    "autist",
    "baby boo",
    "baddie",
    "baka",
    "balls",
    "band kid",
    "bb28",
    "bbnaija",
    "bearposting",
    "belle",
    "belt",
    "beta",
    "big money man",
    "bini",
    "bini_signals_worldtour_2026",
    "binixsummersonic2026",
    "bird hands",
    "birdgender",
    "black",
    "bloat",
    "braindead",
    "brainmaxx",
    "breadloser",
    "breakfast",
    "brought-upsy",
    "bsfr",
    "bump the lamp",
    "bunhead",
    "bussy"
]


@pytest.fixture(autouse=True)
def _lexical_only(monkeypatch):
    monkeypatch.setenv("HYPERLEX_VECTOR", "0")
    monkeypatch.setenv("HYPERLEX_OFFLINE", "1")


@pytest.mark.parametrize("term,family", sorted(EXPECTED_FAMILY.items()))
def test_export_term_family_matches_archive(term, family):
    out = match_lineage(term, use_vector=False)
    assert out is not None and out.get("family_id") == family


@pytest.mark.parametrize("term", EXPECTED_NONE)
def test_export_term_without_family_stays_none(term):
    out = match_lineage(term, use_vector=False)
    assert not out or not out.get("family_id")


def test_layout_families_are_eight_plus_none():
    path = ROOT / "scripts" / "shadow" / "hyperlexical" / "layout.py"
    spec = importlib.util.spec_from_file_location("hyperlexical_layout_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fams = tuple(mod.FAMILIES)
    assert fams[-1] == "none" and len(fams) == 9
    assert fams[:-1] == (
        "betting-sharp", "crypto-degen", "ai-native", "brainrot-aura",
        "kinship-address", "political-status", "gaming-meta", "workplace-corp",
    )
    from hyperlex.analysis import LINEAGE_REGISTRY

    assert {e["family_id"] for e in LINEAGE_REGISTRY} == set(fams[:-1])
