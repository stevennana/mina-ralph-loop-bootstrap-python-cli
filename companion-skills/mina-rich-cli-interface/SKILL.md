---
name: mina-rich-cli-interface
description: Use when a Mina-bootstrapped Python CLI repository needs a Rich-based terminal interface, including Tables, Panels, Progress, Live updates, Rich logging, tracebacks, and stable operator-facing output under a Typer CLI.
---

# Mina Rich CLI Interface

This skill is inspired by the Rich documentation, the Rich GitHub repository, and `rich-cli`, but adapted to the Mina Python CLI bootstrap contract.

Use this skill when a Mina-generated Python CLI repo needs deliberate Rich-powered terminal UX instead of plain text output alone.

## Assumptions

- the repo uses `uv`
- the CLI surface is built with Typer
- `pyproject.toml` owns runtime dependencies
- when a Rich CLI interface is chosen, `rich` is an essential runtime dependency
- CLI E2E tests may need stable output assertions even when Rich is used

## Workflow

1. Read the current CLI docs, command flows, and operator-visible outputs first.
2. Decide which surfaces should remain plain/stable and which benefit from Rich formatting.
3. Confirm `rich` is present in runtime dependencies before implementing Rich UI behavior.
4. Shape output around operator tasks using the smallest Rich primitive that helps.
5. Update docs and CLI E2E coverage when Rich changes visible command behavior.

## Preferred Rich Primitives

- `Console` for structured status and styled text
- `Table` for dense, scan-friendly listings
- `Panel` for summaries and scoped status blocks
- `Progress` for long-running feedback
- `Live` only when live-updating output is genuinely useful
- Rich logging and Rich tracebacks for debugging and operator diagnostics

## Guardrails

- do not replace machine-relevant output with decorative formatting
- do not use `Live` or animation where snapshot-like output is more stable
- prefer stable labels and semantics so CLI tests remain deterministic
- use Rich to clarify operator workflows, not to make the terminal busy
