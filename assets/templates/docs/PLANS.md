# PLANS.md

## Purpose
Execution plans are the main planning unit in this repository.

Before writing or revising plans:

- review the related product, CLI surface, architecture, and design docs first
- improve those supporting docs if the plan would otherwise need to guess
- keep each active plan page focused on one small feature slice
- review each active plan page on its own before considering the queue ready

## Promotion Rules
- Required commands in a task's `taskmeta` are hard gates.
- Failing tests block promotion even if the feature appears complete by inspection.
- Evaluator judgment exists to catch false positives after checks pass, not to excuse red checks.
- If a feature depends on an outside resource, include CLI E2E coverage for that feature before promotion.
- If the same environment-specific blocker repeats three times, branch into a dedicated RCA/fix exec-plan and then return to the original task.

## When The Current Queue Is Done
- Re-enter through docs first: update the relevant product specs and design docs before writing the next tasks.
- Preserve completed plans as history and seed a new active sequence for the next feature wave.
