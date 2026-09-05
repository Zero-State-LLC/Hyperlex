Follow [AGENTS.md](AGENTS.md). That file is the only contributor and agent instruction source in this repository.
For a non-trivial change, read the active intent.md before editing. If none exists, draft intent.md and wait for human accept.

---

## Claude Code host (additive)

When using Claude Code as an additional host (Hermes remains primary), see
[`docs/claude-skill.md`](docs/claude-skill.md) and
[`references/claude-runtime-contract.md`](references/claude-runtime-contract.md).
Install helpers: `bash install.sh --claude` / `--claude-plugin`.
Wrapper: `bash scripts/claude_hlx.sh <command>`.

AGENTS.md remains the only contributor/agent instruction source for this org repo.
