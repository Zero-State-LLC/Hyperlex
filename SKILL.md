---
name: hyperlex
description: Catch slang while it is still becoming culture.
version: 0.4.1
author: Daniel Meyer (scrimshawlife-ctrl), Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags:
      - Memetics
      - Slang
      - Hyperstition
      - Virality
      - Lineage
      - Calibration
      - Brier
      - Receipts
      - Forecasting
    related_skills: []
    category: analysis
  openclaw:
    requires:
      bins: [python3]
    os: [darwin, linux]
    emoji: "🌀"
---

# Hyperlex

Hyperlex is a Hermes skill for memetic emergence analysis: slang detection, lineage matching, virality and hyperstition scoring, integrity-hashed receipts, and Brier calibration after operator settlement. It does not invent numeric Brier on open analysis. Applied Alchemy Labs built the Python package under `src/hyperlex/`; the CLI is `scripts/hyperlex.py`. Baseline `mock` mode needs no network and no Abraxas import.

Hermes substitutes `${HERMES_SKILL_DIR}` with the installed skill directory. Call the bundled CLI through the Hermes `terminal` tool, not as a bare shell aside.

## When to Use

- Detect slang or neologisms and score virality, memetics, or hyperstition
- Match slang into historical lineage families with a transparent confidence breakdown
- Backfill YTD slang packs and backpropagate lineage onto historical receipts (report only; non-mutating)
- Run Phase 5 cultural-transmission simulation (always SPECULATIVE; `brier: null`)
- Propose advisory `LIVE_EMERGENCE_SCAN` cadence with `risk-schedule` (never auto-register Hermes cron)
- Emit integrity-hashed receipts and extract forecast probabilities
- Settle forecasts as an operator and recompute Brier series from the score log
- Scan betting-sharp, crypto-degen, ai-native, brainrot, kinship, or political-status families

Don't use for general web research, product audits, cinematic continuity, or symbolic architecture mapping.

## Prerequisites

- Python 3.10+ with `python3` on PATH
- Optional: `requests`, `jsonschema`, `crawl4ai` for richer ingest and validation
- Optional: network for non-`mock` sources
- Offline force: `HYPERLEX_OFFLINE=1`

## How to Run

After `skill_view` loads this skill, `${HERMES_SKILL_DIR}` is already substituted. Call `terminal`:

```
terminal(command="bash install.sh --dry-run", timeout=60)
terminal(command="bash install.sh", timeout=120)
```

Default install path: `~/.hermes/skills/hyperlex`. Then prove the install:

```
terminal(command="python3 ${HERMES_SKILL_DIR}/scripts/hyperlex.py check", timeout=60)
terminal(command="python3 ${HERMES_SKILL_DIR}/scripts/hyperlex.py smoke", timeout=120)
```

Reuse `HLX="python3 ${HERMES_SKILL_DIR}/scripts/hyperlex.py"` in later `terminal` commands.

## Quick Reference

| Action | `terminal` command |
|--------|-------------------|
| Guided week-one path | `terminal(command="python3 ${HERMES_SKILL_DIR}/scripts/hyperlex.py wizard --auto", timeout=180)` |
| Interactive wizard | `terminal(command="python3 ${HERMES_SKILL_DIR}/scripts/hyperlex.py wizard", timeout=300)` |
| Command map (JSON) | `terminal(command="python3 ${HERMES_SKILL_DIR}/scripts/hyperlex.py commands", timeout=30)` |
| Source and route catalog | `terminal(command="python3 ${HERMES_SKILL_DIR}/scripts/hyperlex.py sources", timeout=30)` |
| Offline pipeline (receipt + forecasts) | `terminal(command="python3 ${HERMES_SKILL_DIR}/scripts/hyperlex.py pipeline \"rizz\" --route offline", timeout=120)` |
| Signal only | `terminal(command="python3 ${HERMES_SKILL_DIR}/scripts/hyperlex.py ingest \"locked in\" --raw-only", timeout=120)` |
| Multi-term atoms | `terminal(command="python3 ${HERMES_SKILL_DIR}/scripts/hyperlex.py pipeline \"sigma rizz locked in\" --route offline", timeout=180)` |
| Open forecasts | `terminal(command="python3 ${HERMES_SKILL_DIR}/scripts/hyperlex.py pending", timeout=30)` |
| Operator settle | `terminal(command="python3 ${HERMES_SKILL_DIR}/scripts/hyperlex.py settle --forecast-id <id> --decision TRUE", timeout=60)` |
| Brier series | `terminal(command="python3 ${HERMES_SKILL_DIR}/scripts/hyperlex.py score-series --mean-shift --verify-chain", timeout=60)` |
| Multi-query scan | `terminal(command="python3 ${HERMES_SKILL_DIR}/scripts/hyperlex.py scan --route offline --receipt --forecasts --append-log", timeout=300)` |
| Advisory schedule only | `terminal(command="python3 ${HERMES_SKILL_DIR}/scripts/hyperlex.py risk-schedule --tier MODERATE --schedule-out /tmp/hlx-cron", timeout=60)` |
| Health | `terminal(command="python3 ${HERMES_SKILL_DIR}/scripts/hyperlex.py doctor", timeout=120)` |

Ingest routing: prefer `--route offline|live|glossary|social` over raw `--source`. Aliases: `real`→glossary, `x`→x_search, `firecrawl`→crawl4ai.

Research commands (still available): `simulate`, `vector-*`, `archive-export`, `lineage-backfill`, `lineage-backprop`, `relay`, `signal`, `diagram`, `ledger-*`. Docs: `docs/operator-loop.md`, `docs/commands.md`.

## Procedure

1. **Onboard.** If the user is new to Hyperlex, call `terminal` with `wizard --auto` (or `wizard --auto --query "<term>"`). Done when the JSON lists step IDs `env_intro`, `doctor`, `demo`, `first_pipeline`, `calibration_coach`, `score_series_hint`, and `handoff`.
2. **Analyze.** Call `terminal` with `pipeline "<query>" --route offline` (or `run` / `ingest`; use `--raw-only` for signal only). Multi-term bags expand to lexicon atoms automatically. Done when a receipt exists and `provenance.brier` is `null`.
3. **Calibrate.** Call `pending`, ask the operator for `TRUE|FALSE|VOID`, then `settle --forecast-id <id> --decision …`, then `score-series --mean-shift --verify-chain`. Never invent Brier. Done when the series status is `SCORED` or `NOT_COMPUTABLE`.
4. **Scan (optional).** Call `scan --route offline --receipt --forecasts --append-log`. For cadence, call `risk-schedule` and write the advisory job under `--schedule-out`. Done when receipts land and no Hermes cron job was registered.
5. **Live ingest.** Use `--route live` (or glossary/social) only when the user allows network. Done when ingest metadata records the intended source and any offline fallback.
6. **Label claims.** Mark findings `OBSERVED`, `INFERRED`, or `SPECULATIVE`. Fail closed on missing outcomes. Done when every numeric score has a matching authority class.
7. **Research.** `simulate`, archive, and vector commands stay optional and SPECULATIVE. Phase 5 packets keep `brier: null`.

Score log default: `~/.hyperlex/score_log.jsonl`. Override with `HYPERLEX_SCORE_LOG`, `--log`, or `--repo-log` → `out/calibration/score_log.jsonl`.

**Authority.** Hyperlex may ingest, match lineage, write receipts and score-log events, compute Brier only from settled pairs, and export Abraxas-compatible ledger shapes (no Abraxas import). Hyperlex may not invent numeric Brier on open analysis, auto-settle without an authority marker, promote speculative hyperstition stages as hard truth, rewrite historical receipt integrity during lineage backprop, invent Brier from Phase 5, or mutate other systems.

**Library path** (when `src/` is on `PYTHONPATH`; the CLI inserts `src/` automatically):

```python
from hyperlex import (
    ingest_signal, fetch_ingest, detect_memetic_patterns,
    match_lineage, emit_receipt, extract_forecasts,
    settle_and_log, recompute_series, score_pair, score_series,
    NOT_COMPUTABLE,
)

result = detect_memetic_patterns(query="rizz", ingest_source="mock")
forecasts = extract_forecasts(result)
# settle_and_log(forecast, outcome_value=1.0, settlement_decision="TRUE")
# recompute_series()
```

## Pitfalls

- Always invoke `scripts/hyperlex.py` through `${HERMES_SKILL_DIR}` so `src/` is first on `sys.path` and the script cannot shadow the package.
- `platforms` is `[linux, macos]`. `install.sh` is bash; Windows is not proven.
- Non-`mock` sources need network and may degrade to mock. Read ingest metadata before treating the source as live.
- Lineage confidence is INFERRED. Do not treat it as observed ground truth.
- `score-series --mean-shift` is advisory for future forecasts only.
- The score log is append-only. Recompute the series from the log; do not treat a stored series as sole truth.
- `risk-schedule` is advisory. Do not add a `metadata.hermes.blueprint` block and do not auto-register cron.

## Verification

Call `terminal`:

```
terminal(command="python3 ${HERMES_SKILL_DIR}/scripts/hyperlex.py check", timeout=60)
terminal(command="python3 ${HERMES_SKILL_DIR}/scripts/hyperlex.py doctor", timeout=120)
terminal(command="python3 ${HERMES_SKILL_DIR}/scripts/hyperlex.py smoke", timeout=120)
```

Optional deeper proof: `ledger-stats`, `signal --input <result.json>`, `feedback --signal-key hyperstition.stage`, `diagram --from-golden --out-dir out/diagrams`, and `scan --config ${HERMES_SKILL_DIR}/examples/cron/scan-queries.json --source mock --receipt --forecasts`.

Successful packaging:

- `~/.hermes/skills/hyperlex/SKILL.md` exists
- `check` returns `"ok": true`
- Frontmatter `description` is ≤60 characters and ends with `.`
- `smoke` writes a receipt under `out/smoke/`
- Open analysis has `"brier": null`

Design references: `DESIGN.md`, `docs/brier-calibration.md`, `docs/slang-lineages.md`, `docs/phase5.md`, `docs/modules/simulation.md`, `schemas/`, `examples/slang-families/`, `data/backfill/2026/`, `references/hermes-runtime-contract.md`.

Local stdlib-first CLI. Baseline (`mock`) needs no network. Real ingest may call public web APIs. Score log and receipts are local files under `~/.hyperlex/` or skill `out/`.
