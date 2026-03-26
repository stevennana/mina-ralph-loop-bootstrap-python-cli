---
name: mina-uv-pytest-unit-testing
description: Use when a Mina-bootstrapped Python CLI repository needs stronger uv-managed pytest guidance for unit, integration, and CLI E2E tiers, CliRunner usage, import or discovery troubleshooting, or keeping make verify aligned with the harness contract.
---

# Mina UV Pytest Unit Testing

Use this skill when a Mina-generated Python CLI repo needs targeted help around pytest setup, test-tier placement, or `uv`-managed test execution.
Read [references/uv-testing-workflow.md](references/uv-testing-workflow.md) when test failures may actually be caused by package layout, environment sync, workspace wiring, or tool-management drift rather than by pytest itself.

## Assumptions

- the repo uses `uv`
- package code lives under `src/<package>/`
- tests are split into `tests/unit`, `tests/integration`, and `tests/e2e`
- CLI E2E tests should prefer Typer/Click `CliRunner`
- `pyproject.toml` owns pytest configuration
- the package-development baseline should follow the `uv init --package` mental model
- `make verify` is a hard promotion gate

## Workflow

1. Read `pyproject.toml`, `Makefile`, and the existing test tree first.
2. Decide which tier the behavior belongs in before adding or moving tests.
3. Run the smallest relevant pytest command under `uv` first.
4. If imports, dependencies, or tools look suspect, use `uv sync` before assuming the tests are wrong.
5. Fix discovery, import, env, or marker problems before broadening coverage.
6. Keep `make test-unit`, `make test-integration`, `make test-e2e`, and `make verify` aligned with the actual test layout.

## Tier Guidance

- unit: pure logic, no hidden filesystem or network coupling
- integration: deliberate runtime-boundary checks such as file-backed storage or worker/runtime seams
- e2e: operator-visible CLI behavior through `CliRunner`, not internal implementation details
- package or workspace issues: read `references/uv-testing-workflow.md` before patching tests around the symptoms

## Troubleshooting Focus

- `src/` import path issues
- environment drift that should be fixed with `uv sync`
- package scaffolding mismatches that violate the `uv init --package` assumptions
- pytest discovery and marker registration problems
- env-var and temp-directory isolation
- workspace dependency wiring problems when the repo grows into a `uv` workspace
- external tool drift when test-related tools are managed with `uv tool install` / `uv tool upgrade`
- brittle CLI output assertions
- E2E tests that should be split into smaller unit or integration checks

## Guardrails

- do not collapse all confidence into one broad E2E test
- do not add network or nondeterministic state to unit tests
- do not treat ad hoc path hacks as the default answer to `src/` import problems
- do not use globally installed tools as a substitute for project test dependencies
- prefer assertions on operator-visible behavior over implementation trivia
- update docs or task contracts when required test commands change
