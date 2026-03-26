---
name: mina-ralph-loop-bootstrap-python-cli
description: Bootstrap or extend a new or early-stage Python CLI repository around a Ralph-style task-promotion loop. Use when Codex needs to interview for product and architecture intent, generate repo-local docs first, scaffold a Python CLI/worker preset, install Ralph loop scripts, and define the initial or next exec-plan wave.
---

# Mina Ralph Loop Bootstrap Python CLI

Build the repository in this order:

1. gather intent until the markdown knowledge base can be written without guessing
2. generate the repo-local docs first
3. scaffold the Python CLI project to match those docs
4. install and adapt the Ralph loop scripts
5. validate the deterministic commands
6. hand back operator guidance

Use this skill for new repositories or very early repositories that still lack a stable docs tree, scaffold contract, and loop harness.
Also use it to extend a repo that was already bootstrapped by this skill when the current queue is complete and the founder wants the next feature wave defined.

## Read First

Read these references before asking questions or writing files:

- [references/harness-engineering.md](references/harness-engineering.md)
- [references/doc-baseline.md](references/doc-baseline.md)
- [references/interview-checklist.md](references/interview-checklist.md)
- [references/python-cli-uv-preset.md](references/python-cli-uv-preset.md)
- [references/expansion-mode.md](references/expansion-mode.md)
- [references/feature-slicing.md](references/feature-slicing.md)
- [references/doc-quality-loop.md](references/doc-quality-loop.md)
- [references/environment-blockers.md](references/environment-blockers.md)
- [references/runtime-startup.md](references/runtime-startup.md)
- [references/operator-logging.md](references/operator-logging.md)

Open templates and copied Ralph assets only when needed:

- `assets/templates/root/`
- `assets/templates/docs/`
- `assets/templates/scaffold/`
- `assets/templates/ralph/`

Use these scripts when bootstrapping:

- `scripts/render_docs.py`
- `scripts/install_scaffold.py`
- `scripts/install_ralph.py`
- `scripts/companion_skills.py`
- `scripts/finalize_bootstrap_state.py`

## Workflow

### 1. Ground the target repo

Inspect the target repository first.

- If the repo is empty, proceed with a fresh bootstrap.
- If the repo already has code, determine whether it is still early enough to be reshaped around generated docs and Ralph scripts.
- If the repo already has the docs tree and Ralph loop installed, determine whether this is a continuation run for the next feature wave instead of a fresh bootstrap.
- Do not install the Ralph loop into a mature repo without first checking whether the existing layout, commands, and docs can support it cleanly.

For continuation runs:

- inspect `docs/exec-plans/active/`
- inspect `docs/exec-plans/completed/`
- inspect the current product specs and design docs
- identify what feature area or operator-visible expansion the founder wants next
- preserve completed plans as history rather than rewriting them

Before making implementation claims or writing replacement code, search the codebase first.
Do not assume a helper, command, adapter, or test is missing just because the first search result was incomplete.

### 1b. Check companion skills before discovery

Before product analysis and before the first substantive founder question, check whether the pinned auto-install companion skill set is already installed under `~/.codex/skills`.
Use `python3 <skill>/scripts/companion_skills.py status` as the source of truth.

Pinned auto-install companion skill for this preset:

- `clean-architecture` for architecture and boundary shaping

Desired later companion skills for this preset are:

- `python-packaging-release` for console entry points, package layout, installability, and publish flow
- `mina-rich-cli-interface` for Rich-powered terminal ergonomics, structured operator output, progress feedback, and tracebacks under a Typer CLI
- `config-and-secrets` for environment-variable contracts, dotenv or secrets-file policy, and settings precedence
- `mina-uv-pytest-unit-testing` for pytest-based unit, integration, and CLI E2E strategy under the Mina Python CLI harness
- `systemd-worker-ops` for long-running service units, restart policy, environment wiring, and log handling

If the user allows companion skills:

- treat this as a startup prerequisite step before product analysis and interview work
- if the pinned skill is already installed, plan to use it during product analysis, interview framing, docs generation, and architecture/spec shaping
- if it is missing, summarize that missing pinned companion skill up front
- ask whether the user wants it auto-installed before product analysis and interview start
- default to the helper installer flow (`python3 <skill>/scripts/companion_skills.py install clean-architecture`) instead of leading with manual clone/copy commands
- print manual clone/copy commands only as fallback guidance, or if the user explicitly asks for manual installation
- do not block the bootstrap if the user declines or skips installation; continue with the built-in workflow
- handle installs one skill at a time before the interview starts
- after the startup install decision is resolved and the product shape is clearer, mention any of the desired later companion skills above only when they are clearly relevant to the repo being bootstrapped
- `mina-rich-cli-interface` is already encoded in this repo and should be installed through `python3 <skill>/scripts/companion_skills.py install mina-rich-cli-interface` when the founder wants a Rich-based CLI interface
- `mina-uv-pytest-unit-testing` is already encoded in this repo and should be installed through `python3 <skill>/scripts/companion_skills.py install mina-uv-pytest-unit-testing` when the founder wants stronger pytest/harness guidance
- the other desired later skills should not be presented as installable until this repo encodes their real upstream repos and pinned install commands
- use `python3 <skill>/scripts/companion_skills.py status` for the startup-default set and `python3 <skill>/scripts/companion_skills.py status --all` when you need to inspect both the startup and later Mina-owned encoded skills

### 2. Interview until the docs are decision-complete

Ask the user questions in stages, not all at once.
Before the first substantive product question, follow this exact startup order:

1. companion skill recommendation and installation decision
2. if the user accepts installs, complete that flow first
3. only after the install decision flow is resolved, begin product analysis/reference review
4. then give the `Plan` mode recommendation
5. then give a short handoff telling the user to say `continue` when ready
6. only after that, ask the first substantive product question

Do not combine the handoff with the first product question.
Do not combine the companion-skill installation decision with the `continue` handoff in the same prompt.
Do not repeat the startup guidance twice.
At the startup handoff stage, do not ask for product intent yet; wait for the user to say `continue` or otherwise clearly indicate readiness.

The interview must make the test strategy explicit before scaffolding starts.
Do not accept vague answers like “we should have decent coverage” or “we can add tests later.”

You need a clear statement of:

- project name and one-line definition
- primary user and target problem
- v1 scope and explicit non-goals
- core entities and relationships
- command groups and primary operator flows
- storage/runtime constraints
- quality bar, unit coverage expectations, and required CLI E2E flows
- any special security or reliability constraints

If a feature depends on an outside resource such as AI chat, a third-party API, email delivery, remote storage, or another integration, require that feature to appear in an E2E scenario before the related task can promote.

For continuation runs, do a delta interview rather than repeating the full bootstrap interview.
Ask only what is needed to define the next feature tranche and its tests without guessing.

Use [references/interview-checklist.md](references/interview-checklist.md) as the stop condition.
Do not start writing the docs until the answers are sufficient to fill the required markdown set in [references/doc-baseline.md](references/doc-baseline.md).
If the test strategy is still ambiguous, keep asking.
For continuation runs, also use [references/expansion-mode.md](references/expansion-mode.md) to decide whether the next wave is specific enough to write new specs and active plans.

### 3. Materialize the docs tree first

Create a temporary answers JSON file from the interview.

- Prefer `/tmp/ralph-bootstrap-answers.json` unless the user wants answers stored in-repo.
- Use uppercase snake-case keys that match the template placeholders.
- Keep multiline sections as markdown-ready strings.

Render the baseline templates:

```bash
python3 <skill>/scripts/render_docs.py --answers /tmp/ralph-bootstrap-answers.json --repo-root <target-repo>
```

Then expand the rendered docs into project-specific content.

- Replace any remaining generic placeholders.
- Add project-specific design docs and product specs beyond the baseline templates whenever the product has more than one distinct feature front.
- If the user provides local or online references, analyze them into `docs/references/` and preserve the useful project-specific takeaways there.
- Ensure `AGENTS.md` stays short and points into the docs tree.
- Ensure active execution plans contain real `taskmeta` blocks and deterministic checks.
- Ensure the docs clearly state that promotion is blocked when required commands fail.
- Use [references/feature-slicing.md](references/feature-slicing.md) to decide how many product specs and executable tasks are needed.

If `FEATURE_SPECS` is present and `EXEC_TASKS` is omitted, `scripts/render_docs.py` will derive a queue whose size follows the selected `SLICE_SIZE` and `BACKLOG_DEPTH` controls. Multiple exec-plans may map to the same product spec when that is required to keep the slices narrow.
If `EXEC_TASKS` is provided but still collapses multiple product specs into broad tasks, the renderer should fail instead of silently accepting the queue.

For continuation runs:

- update the existing product specs before adding new active plans
- add or revise design docs when the new feature changes system shape or boundaries
- update quality, reliability, and security docs if the new wave changes their posture
- keep `docs/references/` current when new user-provided references appear
- leave completed plan history intact
- stop after the docs and next active queue are refreshed; do not begin app-code implementation in the same continuation run

### 3b. Improve supporting docs before writing exec-plans

Before writing or revising exec-plans:

- review the relevant product, CLI surface, architecture, and design docs together
- enhance those docs if the feature description is still rough
- use installed companion skills during design and architecture work when they are available and relevant
- do not create exec-plan pages from weak supporting docs

### 3c. Generate smaller exec-plan pages

Create exec-plan pages only after the supporting docs are sufficiently detailed.

Rules:

- create one exec-plan page per small feature slice
- avoid broad milestone-style scopes
- keep each non-hardening plan focused on one feature front
- allow multiple exec-plan pages to point at the same product spec when that keeps the work narrow
- review each exec-plan page individually before handoff

### 4. Scaffold the Python CLI preset

The generated preset should default to:

- Python with `uv`
- `typer` for CLI composition
- `rich` for terminal UX
- `pydantic` and `pydantic-settings` for config and validation
- a clean architecture with `domain`, `application`, `infrastructure`, `cli`, and `worker` boundaries
- a pluggable storage port with a default local adapter
- a sample task-queue vertical slice
- deterministic command targets implemented through `make` wrappers over `uv run ...`
- predefined harness config in `pyproject.toml` for pytest, Ruff, mypy, and console entry points
- a generated `Makefile`, `src/<package>/` layout, `.env.example`, and baseline tests for unit, integration, and CLI E2E coverage

Required generated operator/developer commands:

- `make lint`
- `make typecheck`
- `make test-unit`
- `make test-integration`
- `make test-e2e`
- `make test`
- `make verify`
- `make worker-smoke`
- `make worker-logged`

If the repo shape needs a different command surface, update the generated docs and Ralph assets immediately so the contract stays consistent.

Install the scaffold with:

```bash
python3 <skill>/scripts/install_scaffold.py --repo-root <target-repo> --answers /tmp/ralph-bootstrap-answers.json
```

### 5. Install and adapt Ralph

Install the copied Ralph assets with:

```bash
python3 <skill>/scripts/install_ralph.py --repo-root <target-repo> --answers /tmp/ralph-bootstrap-answers.json
```

Adapt the copied scripts so they match the generated repo:

- required commands must match the generated Makefile and `uv` workflow
- evaluator and promotion logic must treat failing commands as hard gates
- worker/runtime startup guidance must match the CLI/worker process model
- operator logging must refer to the logged worker path, not a web-style runtime

### 6. Bootstrap boundary

The initial bootstrap session should only guarantee the harness environment:

- docs rendered and tightened
- minimal scaffold in place
- Ralph installed and aligned
- deterministic commands documented and working
- runtime startup proven when the app depends on persistent state
- bootstrap foundation task archived into `docs/exec-plans/completed/`
- remaining feature tasks left in `docs/exec-plans/active/` for the Ralph loop

Do not pre-execute the queued feature tasks during the initial bootstrap run.

### 7. Continuation runs

Use the same skill later to plan the next feature wave:

1. inspect completed plans and current specs
2. interview only for the next feature delta
3. update product specs and design docs first
4. create the next active exec-plans
5. keep the same promotion rules and required command gates
6. stop there

Important continuation boundary:

- refresh docs and create the next exec-plan wave
- do not start application-code implementation in the same continuation pass
