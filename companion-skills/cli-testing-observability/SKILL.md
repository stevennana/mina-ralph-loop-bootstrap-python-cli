---
name: cli-testing-observability
description: Use when a Python CLI project needs stronger pytest guidance for unit, integration, and CLI E2E coverage, CliRunner usage, log assertions, or operator-visible observability defaults.
---

# CLI Testing Observability

Use this skill when the harness needs more than a minimal smoke test.

## Focus

- pytest test-tier boundaries
- Typer/Click `CliRunner` coverage
- fixtures for temp state, env vars, and runtime isolation
- log assertions, caplog usage, and failure diagnostics
- keeping `make verify` meaningful and deterministic

## Workflow

1. Inspect the current command surface, worker path, and required promotion gates.
2. Decide what belongs in unit, integration, and E2E layers.
3. Keep CLI tests narrow and operator-visible.
4. Make logging and failure output easy to inspect when a loop stalls.
5. Tighten tests before adding prompt complexity when the same bug repeats.

## Guardrails

- Do not collapse all coverage into one broad E2E test.
- Avoid hidden network or filesystem coupling in unit tests.
- Prefer assertions on operator-relevant behavior over implementation trivia.
