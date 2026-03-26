---
name: python-packaging-release
description: Use when a Python CLI project needs concrete packaging and release guidance for pyproject metadata, console entry points, build backends, pipx-friendly installs, or publish workflows.
---

# Python Packaging Release

Use this skill when the repo needs to become an installable Python CLI instead of remaining a local-only app.

## Focus

- `pyproject.toml` metadata that matches the product and command surface
- console-script entry points
- build backend and wheel/sdist shape
- `uv build` and `uv publish` workflow design
- pipx-friendly installation and smoke checks

## Workflow

1. Inspect the current `pyproject.toml`, command entry points, and README/install docs.
2. Decide whether the target is local-only, private distribution, or public PyPI release.
3. Keep package name, import package, and CLI command consistent.
4. Add the minimum release flow needed now; do not overbuild versioning or automation.
5. Update deterministic commands or docs when packaging behavior changes.

## Guardrails

- Do not invent a publish flow if the founder only needs local development.
- Keep secrets such as PyPI tokens or trusted-publisher config out of committed code.
- Prefer one clear install story over multiple partially-supported options.
