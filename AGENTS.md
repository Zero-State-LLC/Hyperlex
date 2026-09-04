# Agent contract — Hyperlex

You are working in **Hyperlex** (`Zero-State-LLC/Hyperlex`), a standalone
Hermes skill. This file is the canonical contract for Cursor, Claude,
Codex, Grok, and OpenClaw. Harness adapters (`CLAUDE.md`) only point here.

`SKILL.md` is the Hermes runtime contract. Do not rewrite it unless an
accepted intent is explicitly the skill-contract change. Do not copy
Noema deploy-worker or pin workflows into this repo.

## Intent

Read the active `intent.md` under [`intent/`](intent/README.md) before
editing. Next stage is `spec.md` / plan — do not skip to code.

If the change is non-trivial and no intent exists, draft one from
[`intent/_TEMPLATE.md`](intent/_TEMPLATE.md) and wait for a human to
accept it. Trivial docs and chore fixes do not need an intent file.

## Commands

| Task | Command |
|---|---|
| Offline demo | `python3 scripts/hyperlex.py demo` |
| Health | `python3 scripts/hyperlex.py check` then `doctor` |
| Smoke | `python3 scripts/hyperlex.py smoke` |
| Tests | `PYTHONPATH=src pytest -q` |
| Install dry-run | `bash install.sh --dry-run` |

Do not invent commands. Prefer `${HERMES_SKILL_DIR}` in Hermes `terminal`
calls. Baseline work uses `--route offline` / `mock`.

## Invariants

- Brier only after operator settlement. Open analysis keeps `brier: null`.
- Phase 5 / simulate / phylogeny stay **SPECULATIVE**.
- Fail closed on missing outcomes. Label `OBSERVED` / `INFERRED` /
  `SPECULATIVE` / `NOT_COMPUTABLE`.
- Do not invent numeric Brier, auto-settle, auto-register Hermes cron, or
  rewrite historical receipt integrity.
- Hyperlex never imports Abraxas. Cron (`risk-schedule`) is advisory only.
- Do not invent CLI behavior `SKILL.md` does not name.
- Do not put secrets, tokens, or live credentials in the tree.
- Do not dispatch leftover Noema-shaped deploy or pin workflows.

## Escalation

If CI, tests, or validators look wrong — missing coverage, silent skips,
green-but-inert checks, or a suite that contradicts the skill contract:

1. Open a bounded defect issue labeled `bug`.
2. Do **not** patch tests, fixtures, or CI to force green.
3. Do **not** weaken an assertion or rewrite `SKILL.md` to match a
   broken path.

A red honest check is better than a green lie.

Owner-gated (human yes): operator settlement, live ingest, cron
registration, official Hermes hub submit, license/legal, and spend.
Agents do not buy things or publish the skill as official.

## Team context

Org and partner status is not this repo. When a task needs it, load
[Zero-State-LLC/agent-context](https://github.com/Zero-State-LLC/agent-context):

1. `HANDOFF.md`
2. `STATUS.md`
3. `DECISIONS.md` only if a prior choice affects this task

Clone: `gh repo clone Zero-State-LLC/agent-context ~/agent-context`.
Pull `--ff-only` before trusting a local copy.

## Skills

Name only skills that already exist. Do not invent skills or bots.
The Hermes skill in this repo is `hyperlex` (`SKILL.md`).
