# AGENTS.md

## Purpose
{{PROJECT_NAME}} is a {{ONE_LINE_PRODUCT}}.

This repository is optimized for agent-legible development and a Ralph-style task-promotion loop.

## Read Order
Before changing code or plans, read these files in order:

1. `ARCHITECTURE.md`
2. `docs/PRODUCT_SENSE.md`
3. `docs/design-docs/core-beliefs.md`
4. `docs/product-specs/index.md`
5. `docs/CLI_SURFACE.md`
6. `docs/PLANS.md`
7. active plans in `docs/exec-plans/active/`

## Scope Guardrails
### In scope for v1
{{V1_SCOPE_BULLETS}}

### Explicitly out of scope for v1
{{NON_GOALS_BULLETS}}

## Validation Strategy
Use layered checks:
- unit tests for domain rules
- integration tests for repository/runtime boundaries where needed
- small CLI E2E coverage for the required flows only

Promotion is blocked when required checks fail. Required commands in active task contracts are hard gates, not suggestions.
While iterating, prefer the smallest targeted check for the code you just changed. Use the full required command set before considering the task done.
If a feature depends on an outside resource such as AI or another remote service, keep it in the required CLI E2E flows before allowing promotion.
For manual process inspection, prefer `make worker-logged` and set `LOG_LEVEL` intentionally instead of relying only on ephemeral terminal output.

### Required E2E flows
{{REQUIRED_E2E_BULLETS}}

## Search Discipline
- Search the codebase before concluding that a thing is unimplemented.
- Prefer multiple targeted searches over one broad assumption.
- If you find a partial implementation, adapt or complete it instead of duplicating it blindly.

## Documentation Discipline
- If behavior changes, update the related spec or design doc in the same cycle.
- Prefer small, executable plans over vague TODOs.
- When a repeated mistake appears, first document it; if it keeps recurring, promote it into tests or lint rules.
- Keep the documented test strategy current; do not leave promotion gates implied.
- When adding or editing tests, explain what behavior the test protects if that intent would otherwise be easy to lose.

## Optional Companion Skills
- If the customer allows them and they are installed, consider relevant companion skills before planning or implementation.
- Good candidates include clean-architecture and other skills directly relevant to the chosen integrations.

## Done Definition
{{DONE_DEFINITION}}
