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
- `assets/templates/ralph/`

Use these scripts when bootstrapping:

- `scripts/render_docs.py`
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

Before making implementation claims or writing replacement code, search the codebase first.
Do not assume a helper, command, adapter, or test is missing just because the first search result was incomplete.

### 1b. Check companion skills before discovery

Before product analysis and before the first substantive founder question, check whether the pinned companion skill set is already installed under `~/.codex/skills`.
Use `python3 <skill>/scripts/companion_skills.py status` as the source of truth.

Recommended companion skill for this preset:

- `clean-architecture` for architecture and boundary shaping

If the skill is missing:

- summarize the missing skill up front
- ask whether the user wants it auto-installed before product analysis starts
- default to the helper installer flow
- do not block the bootstrap if the user declines

### 2. Interview until the docs are decision-complete

Ask the user questions in stages, not all at once.
Before the first substantive product question, follow this startup order:

1. companion skill recommendation and installation decision
2. if the user accepts installs, complete that flow first
3. then give the `Plan` mode recommendation
4. then give a short handoff telling the user to say `continue` when ready
5. only after that, ask the first substantive product question

Do not combine the handoff with the first product question.
Do not combine the companion-skill installation decision with the `continue` handoff in the same prompt.

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

Use [references/interview-checklist.md](references/interview-checklist.md) as the stop condition.
Do not start writing the docs until the answers are sufficient to fill the required markdown set in [references/doc-baseline.md](references/doc-baseline.md).

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
- If the user provides local or online references, analyze them into `docs/references/`.
- Ensure `AGENTS.md` stays short and points into the docs tree.
- Ensure active execution plans contain real `taskmeta` blocks and deterministic checks.
- Ensure the docs clearly state that promotion is blocked when required commands fail.

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
