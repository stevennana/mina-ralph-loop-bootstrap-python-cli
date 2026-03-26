---
name: mina-uv-pytest-unit-testing
description: Use when a Mina-bootstrapped Python CLI repository needs stronger uv-managed pytest guidance for unit, integration, and CLI E2E tiers, CliRunner usage, import or discovery troubleshooting, or keeping make verify aligned with the harness contract.
---

# Mina UV Pytest Unit Testing

This skill is inspired by `uv-pytest-unit-testing` from `gaelic-ghost/python-skills`, but adapted to the Mina Python CLI bootstrap contract.

Use this skill when a Mina-generated Python CLI repo needs targeted help around pytest setup, test-tier placement, or `uv`-managed test execution.

## Assumptions

- the repo uses `uv`
- package code lives under `src/<package>/`
- tests are split into `tests/unit`, `tests/integration`, and `tests/e2e`
- CLI E2E tests should prefer Typer/Click `CliRunner`
- `pyproject.toml` owns pytest configuration
- `make verify` is a hard promotion gate

## Workflow

1. Read `pyproject.toml`, `Makefile`, and the existing test tree first.
2. Decide which tier the behavior belongs in before adding or moving tests.
3. Run the smallest relevant pytest command under `uv` first.
4. Fix discovery, import, env, or marker problems before broadening coverage.
5. Keep `make test-unit`, `make test-integration`, `make test-e2e`, and `make verify` aligned with the actual test layout.

## Tier Guidance

- unit: pure logic, no hidden filesystem or network coupling
- integration: deliberate runtime-boundary checks such as file-backed storage or worker/runtime seams
- e2e: operator-visible CLI behavior through `CliRunner`, not internal implementation details

## Troubleshooting Focus

- `src/` import path issues
- pytest discovery and marker registration problems
- env-var and temp-directory isolation
- brittle CLI output assertions
- E2E tests that should be split into smaller unit or integration checks

## Guardrails

- do not collapse all confidence into one broad E2E test
- do not add network or nondeterministic state to unit tests
- prefer assertions on operator-visible behavior over implementation trivia
- update docs or task contracts when required test commands change
