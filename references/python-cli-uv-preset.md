# Python CLI UV Preset

This skill's first version supports one opinionated scaffold only.

## Stack

- Python
- `uv`
- Typer
- Rich
- Pydantic + Pydantic Settings
- pytest
- Ruff
- mypy
- Makefile command wrappers

## Required commands

The generated repo should expose:

- `make lint`
- `make typecheck`
- `make test-unit`
- `make test-integration`
- `make test-e2e`
- `make test`
- `make verify`
- `make worker-smoke`
- `make worker-logged`

Recommended shape:

- `make lint` -> `uv run ruff check .`
- `make typecheck` -> `uv run mypy src`
- `make test-unit` -> `uv run pytest tests/unit`
- `make test-integration` -> `uv run pytest tests/integration`
- `make test-e2e` -> `uv run pytest tests/e2e`
- `make test` -> run all test tiers
- `make verify` -> lint + typecheck + full tests
- `make worker-smoke` -> prove runtime preparation and a production-style worker entrypoint
- `make worker-logged` -> run the normal long-lived worker path and tee stdout/stderr to `logs/`

For this skill, `make verify` is not advisory. Generated task contracts should treat the required test-bearing commands as hard promotion gates.

## Minimum scaffold

- one multi-command Typer CLI
- one minimal domain/service path
- a pluggable storage boundary with a default local adapter
- one unit test
- one CLI E2E smoke test
- deterministic commands wired before the Ralph loop is considered ready
- if the app uses persistent runtime state, a worker smoke proves the runtime path is viable
- the repo exposes `make worker-logged` so operators can inspect real process behavior

## Ralph alignment

Keep these defaults aligned unless there is a strong reason not to:

- docs tree rooted at `docs/`
- task queue at `docs/exec-plans/active/`
- state under `state/`
- Ralph scripts under `scripts/ralph/`

## Adaptation Rules

- If the scaffold's commands differ, update the copied Ralph scripts immediately.
- Do not leave the repo in a state where the docs prescribe one command contract and the scaffold exposes another.
- Do not leave the repo in a state where the evaluator can promote tasks despite failing required commands.
- Ensure external-resource features are represented in CLI E2E coverage before the related task is promotable.
- If the app depends on DB or runtime preparation, do not leave the worker path unproven.
- Do not leave operators blind during manual verification; wire `make worker-logged`, `logs/`, and log-level configuration into the generated repo contract.
