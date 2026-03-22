# AGENT.md

## Purpose

This repository defines the Codex skill `mina-ralph-loop-bootstrap-python`.

The skill bootstraps a brand new or very early-stage repository into a docs-first, Ralph-style task-promotion repo using a fixed Python CLI preset:

- Python
- `uv`
- Typer CLI
- pytest-based testing
- Makefile command wrappers
- a long-running worker path that can be supervised by `systemd`

This file is for contributors improving the skill itself, not for generated application repos.

## What Must Stay True

When enhancing this skill, preserve these invariants:

- Docs come before scaffold generation.
- The interview must produce a concrete test strategy before docs are considered complete.
- The preferred interview style is one question at a time, with suggested options and a free-form fallback.
- At interview start, the skill should recommend `Plan` mode when the user wants selectable option-list UX.
- At interview start, the skill should handle companion-skill guidance first, then `Plan` mode guidance, then a `continue` handoff before asking the first product question.
- The same skill should support later feature expansion by updating docs first and seeding the next exec-plan wave.
- Continuation runs are planning-only by default.
- The supported stack stays intentionally narrow unless the skill contract is explicitly expanded.
- `SKILL.md` remains the operating contract for another Codex instance.
- The references define stop conditions and baseline requirements; code and templates must agree with them.
- Generated repos must expose deterministic commands for lint, typecheck, unit tests, integration tests, CLI E2E tests, verification, worker smoke, and logged worker startup.
- Multiple feature fronts should not collapse into one generic product spec and one oversized first-slice task.
- Failing required commands block promotion; evaluator judgment does not override red checks.
- External-resource features should require E2E coverage before promotion.
- Optional companion skills should be considered only when the user allows them and they are actually installed.
- The bootstrap session must stop after foundation completion and must not pre-execute queued feature tasks.
- Expansion sessions must stop after the next-wave docs and exec-plans are refreshed.
- Completed tasks belong in `docs/exec-plans/completed/`, not `active/`.
- Stateful generated repos should prove their worker/runtime startup path explicitly, not just pass lint or tests.
- Generated repos should expose an operator-visible `make worker-logged` path, a `logs/` directory, and configurable process log levels for manual debugging.

## Read Order

Before changing behavior, read these files in order:

1. `SKILL.md`
2. `references/harness-engineering.md`
3. `references/doc-baseline.md`
4. `references/interview-checklist.md`
5. `references/feature-slicing.md`
6. `references/python-cli-uv-preset.md`
7. `references/operator-logging.md`
8. `scripts/render_docs.py`
9. `scripts/install_ralph.py`
10. `scripts/companion_skills.py`
11. the relevant files under `assets/templates/`

## Enhancement Rules

- Update the contract first when behavior changes materially.
- Keep templates and references synchronized.
- Keep placeholder names stable and uppercase snake case unless a migration is intentional.
- If you change command names, repo paths, or runtime expectations, update the preset reference and Ralph assets together.
- Do not broaden this into a generic multi-framework bootstrapper by accident.
