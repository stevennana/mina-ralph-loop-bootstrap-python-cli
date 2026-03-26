# mina-ralph-loop-bootstrap-python-cli

`mina-ralph-loop-bootstrap-python-cli` is a Codex skill for bootstrapping or extending a brand new or very early-stage Python CLI repository into a docs-first Ralph-style task-promotion repo.

The first version is intentionally opinionated. It supports one primary preset:

- Python
- `uv`
- Typer CLI
- clean architecture with a pluggable storage boundary
- pytest-based unit, integration, and CLI E2E testing
- a long-running worker command that can be supervised by `systemd`

Its job is to:

1. interview the founder until product and architecture ambiguity is removed
2. generate a repo-local markdown knowledge base
3. scaffold the initial Python CLI app to match those docs
4. install and adapt Ralph loop scripts
5. seed an initial active task queue with deterministic checks
6. document how to run one cycle or an unattended loop
7. re-enter a bootstrapped repo later to define the next feature wave and its exec-plans

## Harness Flow

This skill follows the same harness-engineering model as the original web bootstrap skill:

- the repository is the system of record
- `AGENTS.md` in generated repos stays short and points into `docs/`
- product, architecture, quality, reliability, security, and plans live in markdown
- active tasks are executable contracts with `taskmeta`
- promotion depends on deterministic checks plus a separate evaluator step
- failing required commands block promotion

It also keeps the practical Ralph rules:

- search the codebase before assuming something is missing
- keep tasks narrow and promotion-oriented
- prefer targeted checks while iterating, then use the required commands as the promotion gate
- if a feature depends on an outside resource, require CLI E2E coverage before promotion
- if the same environment-specific blocker repeats three times, auto-branch it into an RCA/fix exec-plan and return to the parent task after promotion
- if the app has persistent runtime state, prove the worker/runtime startup path explicitly instead of assuming typecheck or tests are enough

## Repository Layout

- `SKILL.md`: operating contract for Codex
- `references/`: harness model, doc baseline, interview checklist, Python CLI preset, and continuation rules
- `scripts/render_docs.py`: renders the baseline docs into a target repo
- `scripts/install_ralph.py`: installs the Ralph assets into a target repo
- `scripts/companion_skills.py`: checks, prints commands for, and installs the pinned companion skills
- `scripts/finalize_bootstrap_state.py`: archives the completed foundation task and leaves feature tasks queued for Ralph
- `assets/templates/root/`: root-file templates
- `assets/templates/docs/`: docs-tree templates for Python CLI repos
- `assets/templates/ralph/`: Ralph loop adaptation base copied into target repos

## Generated Repo Contract

Generated repositories should be docs-first Python CLI projects with:

- `uv` for package and environment management
- `typer`, `rich`, `pydantic`, and `pydantic-settings` for the default CLI/runtime shape
- a layered `src/<package>/` layout with `domain`, `application`, `infrastructure`, `cli`, and `worker` boundaries
- a sample task-queue workflow that proves a real CLI slice
- deterministic command targets such as:
  - `make lint`
  - `make typecheck`
  - `make test-unit`
  - `make test-integration`
  - `make test-e2e`
  - `make verify`
  - `make worker-smoke`
  - `make worker-logged`

The `make` targets are wrappers over `uv run ...` commands so operators get short, consistent promotion gates on macOS and Linux.

## Workflow

The skill is meant to run in this order:

1. inspect the target repo
2. interview the founder until the docs can be written without guessing
3. map the distinct user-visible or operator-visible features that need their own specs and task slices
4. render the baseline docs tree
5. expand those docs into project-specific material
6. improve the supporting architecture/design/product docs until they are specific enough
7. generate smaller exec-plan pages for individual features
8. review each exec-plan page one by one and loop on quality if needed
9. scaffold the Python CLI app to match the docs
10. install and adapt the Ralph loop
11. finalize the bootstrap task state without running feature tasks
12. seed the initial active task queue
13. validate commands and hand back operator guidance

## Limitations

Current v1 limitations:

- optimized for empty or very early repositories
- intentionally centered on Python CLI/worker repos, not web apps
- not yet a generic multi-runtime bootstrapper
- copied Ralph assets are a starting point, not guaranteed drop-ins
- generated docs may still need project-specific rewriting after first render

## Companion Skills

The pinned auto-install companion-skill recommendation for this preset is:

- `clean-architecture` for boundary shaping and layered application design

The bootstrap should check whether that skill is already installed before deeper product analysis starts, ask whether to auto-install it before the interview begins, default to the helper installer flow, and keep the pinned manual commands correct as fallback guidance.

Additional companion-skill areas that are often useful for Python CLI repos should be recommended when relevant, but are not treated as auto-installable until this skill has stable upstream install sources encoded for them:

- `python-packaging-release` for console entry points, package layout, installability, and publish workflow design
- `cli-ux-typer-rich` for Typer command trees, shell completion, Rich output patterns, and terminal ergonomics
- `config-and-secrets` for settings precedence, dotenv support, and secret-source policy
- `cli-testing-observability` for pytest CLI E2E strategy, logging assertions, and operator-visible diagnostics
- `systemd-worker-ops` for long-running worker service units, restart behavior, and runtime log handling

## Stall triage

Generated Ralph loops use a compact health line in `state/run-log.md`:

- `o` = promoted success
- `x` = completed non-promotion, failure, or RCA auto-branch
- `!` = worker stalled during that cycle

Only repeated environment-specific blockers on the same task should branch into the RCA/fix exec-plan flow, and generated loops now auto-create that RCA task on the third identical blocker.

## Enable The Skill In A New Codex Project

From any shell:

```bash
mkdir -p ~/.codex/skills
ln -s /absolute/path/to/mina-ralph-loop-bootstrap-python-cli ~/.codex/skills/mina-ralph-loop-bootstrap-python-cli
```

For this repository specifically:

```bash
ln -s /Users/stevenna/PycharmProjects/mina-ralph-loop-bootstrap-python-cli ~/.codex/skills/mina-ralph-loop-bootstrap-python-cli
```

Then start a Codex session in the target repository and prompt:

```text
Use $mina-ralph-loop-bootstrap-python-cli to bootstrap this repository into a docs-first Ralph-style Python CLI project.
```
