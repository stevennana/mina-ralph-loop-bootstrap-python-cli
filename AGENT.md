# AGENT.md

## Purpose

This repository defines the Codex skill `mina-ralph-loop-bootstrap-python-cli`.

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
- The companion-skill install decision should happen before deep product/reference review.
- The companion-skill installation decision and the `continue` handoff should happen in separate prompts.
- The same skill should support later feature expansion by updating docs first and seeding the next exec-plan wave.
- Continuation runs are planning-only by default: refresh docs and the next exec-plan wave, then stop before application-code implementation starts.
- The supported stack stays intentionally narrow unless the skill contract is explicitly expanded.
- `SKILL.md` remains the operating contract for another Codex instance.
- The references define stop conditions and baseline requirements; code and templates must agree with them.
- Generated repos must expose deterministic commands for lint, typecheck, unit tests, integration tests, CLI E2E tests, verification, worker smoke, and logged worker startup.
- Multiple feature fronts should not collapse into one generic product spec and one oversized first-slice task.
- Each non-hardening executable task should usually map to exactly one product spec.
- A single product spec may legitimately map to multiple non-hardening exec-plans when that keeps the slices narrow.
- Failing required commands block promotion; evaluator judgment does not override red checks.
- External-resource features should require E2E coverage before promotion.
- Contributors should strengthen search-before-change behavior and avoid assumptions that code is missing.
- Tests should explain the behavior they protect when that context would otherwise be lost across loops.
- Optional companion skills should be considered only when the user allows them and they are actually installed.
- The pinned companion skill set should be checked and recommended before product analysis, founder discovery, and docs are written.
- The pinned auto-install companion skill set remains intentionally narrow until additional skills have stable install sources and verified commands.
- If relevant companion skills are missing, the startup guidance should ask about auto-install first, use the helper installer by default, and keep the manual commands correct as fallback guidance.
- The startup guidance should use the pinned manual install commands from this skill, not guessed catalog paths.
- The startup guidance should be emitted once, not duplicated.
- The startup guidance should summarize all relevant missing companion skills before asking about installation.
- Companion-skill installs should be proposed and run one skill at a time before the interview starts.
- The default startup install path should be the helper installer script, with manual commands as fallback only.
- The skill should also recommend relevant non-pinned companion skill areas for Python CLI repos, especially packaging/release, CLI UX, config/secrets, testing/observability, and worker operations, but should not present them as auto-installable unless real install sources are encoded.
- When `FEATURE_SPECS` is present and `EXEC_TASKS` is omitted, the derived queue should follow explicit slice-size and backlog-depth controls instead of stopping at one task per feature spec.
- When the founder does not specify queue sizing controls, the defaults should be `SLICE_SIZE=balanced` and `BACKLOG_DEPTH=10-15 tasks`.
- Supporting architecture/design/product docs should be strengthened before exec-plan pages are written.
- Each exec-plan page should be reviewed individually for detail and scope quality.
- If doc quality is still weak, loop on docs and plans; if the blocker is missing intent, go back to interview.
- If the same environment-specific blocker repeats three times, create a dedicated RCA/fix exec-plan automatically and then return to the original task through normal promotion.
- Generated Ralph loops may offer a manual promotion path for exceptional stalled-but-done cases, but it must require an explicit reason and record that override durably in task history.
- User-provided references should be analyzed into `docs/references/` and preserved as durable project knowledge.
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
