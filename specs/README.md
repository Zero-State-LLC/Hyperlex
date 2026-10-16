# Hyperlex Spec Kit

Constitution: `.specify/memory/constitution.md` (v1.0.0, **SHADOW** until operator promotion)

| ID | Title | SDD status | Runtime on main |
|----|-------|------------|-----------------|
| 000 | Hyperlex spine (as-built v0.4.0) | SPECIFY locked | shipping |
| 001 | Mutation grammar detector | CLARIFY locked · implement on main · not CONVERGED | `hyperlex.mutation` + tests |
| 002 | Hermes command surface | SPECIFY locked · implement partial | package CLI + `hlx-mutation` + `hyperlex init` |
| 003 | Mutation detect v0.2 | SPECIFY locked · implement SHADOW | GAME_ENCODE / CODE_SWITCH / PHONETIC_WARP + watch jsonl + `--human` |
| 008 | Lexical emergence | SPECIFY draft · SHADOW · merged with Danny's yes 2026-10-16 (CR-5 amended by 009) | docs + contracts only |
| 009 | Ruling label taxonomy (S/O/U/R) | SPECIFY · SHADOW · decisions Q1-Q5 applied 2026-10-16 | `scripts/v2/ruling_queue.py` mirror + tests |

001 extras: `clarify.md`, `threat-model.md`, `owasp-mapping.md`, `checklist.md`, `dual-use-gate.md`, `ux-commands.md`, `schemas/mutation_trace.v0.1.schema.json`

003 extras: `dual-use-gate.md` (L4/L6 detect-only addendum). Packet schema stays `hyperlex.mutation_trace.v0.1`. Constitution stays SHADOW.

Gate: `specs/runtime-ready.md`

Dependency order (DAG), statuses and known problems: [`DAG.md`](DAG.md) · [`index.yaml`](index.yaml). Pre-SDD design docs now live in [`pre-sdd/`](pre-sdd/).

Merged PRs that landed the gate: #6 detector, #7–9 skill alias, #10 wheel, #11 graft-style init.
