# PLANS.md

## Purpose
Execution plans are the main planning unit in this repository.

A plan is not a vague idea. It is an executable work packet with:

- a clearly scoped goal
- explicit non-goals
- ordered implementation steps
- validation criteria
- exit criteria
- linked docs to update
- required commands that prove the task is complete

## How to Use Plans
### Before writing or revising plans
- review the related product, CLI surface, architecture, and design docs first
- improve those supporting docs if the plan would otherwise need to guess
- keep each active plan page focused on one small feature slice
- review each active plan page on its own before considering the queue ready

### During coding
- keep diffs narrow
- update docs when behavior changes
- use the plan as the source of sequencing
- if the plan is wrong, fix the plan first
- search the codebase before assuming a helper or feature is missing
- prefer targeted checks for the unit or slice you just changed

### After coding
- move completed plans to the completed directory
- update quality scores if a domain meaningfully improved
- record debt instead of letting it stay implicit

## Promotion Rules
- Each task's `taskmeta.execution_requirements` declares the worker/evaluator sandbox lane that Ralph should use for that task.
- Required commands in a task's `taskmeta` are hard gates.
- Failing tests block promotion even if the feature appears complete by inspection.
- Evaluator judgment exists to catch false positives after checks pass, not to excuse red checks.
- If the tests do not prove the intended behavior, tighten the task contract and checks before promoting.
- Fast local checks are for iteration speed; the required commands remain the promotion contract.
- If a feature depends on an outside resource, include CLI E2E coverage for that feature before promotion.
- If a task needs live external network access to prove its acceptance path, declare that in `taskmeta.execution_requirements` instead of assuming the default sandbox lane can reach the endpoint.
- If a plan page is still rough or broad, improve the supporting docs and split the plan before promotion work starts.
- If the same environment-specific blocker repeats three times, let the Ralph harness auto-branch into a dedicated RCA/fix exec-plan and then return to the original task through normal promotion.

## When The Current Queue Is Done
- Do not treat an empty active queue as the end of the product.
- Re-enter through docs first: update the relevant product specs and design docs before writing the next tasks.
- Preserve completed plans as history and seed a new active sequence for the next feature wave.
- Make the next tranche ordered, promotion-ready, and sized to the requested backlog depth before implementation begins.
