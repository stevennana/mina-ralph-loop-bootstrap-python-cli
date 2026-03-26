---
name: cli-ux-typer-rich
description: Use when a Python CLI project needs deliberate command-surface and terminal-UX guidance for Typer and Rich, including command grouping, help text, output formatting, completion, and operator ergonomics.
---

# CLI UX Typer Rich

Use this skill when the CLI surface needs more intentional design than "just expose some commands."

## Focus

- Typer command groups, naming, and option shapes
- help text and command discoverability
- stable stdout for operator and test usage
- Rich tables, panels, tracebacks, and logging
- shell completion and human-friendly terminal behavior

## Workflow

1. Read the current CLI docs and real operator flows first.
2. Shape commands around tasks operators actually perform, not around internal module names.
3. Keep machine-relevant output stable where tests or scripts depend on it.
4. Use Rich to improve scanning and diagnostics, not to add noise.
5. Update CLI docs and E2E coverage whenever the command surface changes.

## Guardrails

- Avoid decorative output that makes logs or tests brittle.
- Prefer one obvious command path over multiple aliases.
- Keep error messages actionable and exit behavior deterministic.
