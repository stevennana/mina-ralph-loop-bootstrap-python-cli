# {{PROJECT_NAME}}

{{ONE_LINE_PRODUCT}}

## Development Harness

- `uv` manages the environment and runs the toolchain.
- `make lint` runs Ruff.
- `make typecheck` runs mypy over `src/`.
- `make test-unit`, `make test-integration`, and `make test-e2e` run the three test tiers.
- `make verify` is the promotion gate: lint, typecheck, and all tests.
- `make worker-smoke` proves the worker entrypoint and runtime path can boot.
- `make worker-logged` runs the worker with operator-visible logs under `logs/`.

## Entry Points

- CLI command: `{{CLI_COMMAND_NAME}}`
- Python package: `{{PYTHON_PACKAGE_NAME}}`

## Environment

Copy `.env.example` to `.env` when you want local overrides.
