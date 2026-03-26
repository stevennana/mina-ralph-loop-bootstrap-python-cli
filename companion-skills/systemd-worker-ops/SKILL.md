---
name: systemd-worker-ops
description: Use when a Python CLI project needs concrete worker-operations guidance for systemd services, ExecStart, restart policy, environment files, log handling, shutdown behavior, or production-style worker supervision.
---

# Systemd Worker Ops

Use this skill when the worker path is moving from a local loop to supervised operation.

## Focus

- `systemd` unit design
- `ExecStart`, `WorkingDirectory`, and environment wiring
- restart policy and failure handling
- journald or file-log expectations
- stop behavior, timeouts, and operator runbooks

## Workflow

1. Inspect the current worker command, config model, and logging contract.
2. Make the unit file match the real runtime command instead of a simplified demo path.
3. Keep environment and secret handling outside committed service files where appropriate.
4. Document how operators start, stop, inspect, and debug the worker.
5. Align worker smoke and logged-worker paths with the service behavior.

## Guardrails

- Do not claim production readiness without a real operator startup story.
- Avoid unit files that depend on interactive shells or hidden state.
- Keep restart behavior explicit so crash loops are diagnosable.
