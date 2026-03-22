# Expansion Mode

Use this reference when the repository already has the baseline docs, scaffold, and Ralph loop, but the current queue is complete and the founder wants the next wave of work defined.

## Read First In The Target Repo

Before asking new questions, inspect:

1. `AGENTS.md`
2. `ARCHITECTURE.md`
3. `docs/PRODUCT_SENSE.md`
4. `docs/CLI_SURFACE.md`
5. `docs/PLANS.md`
6. relevant files in `docs/product-specs/`
7. relevant files in `docs/design-docs/`
8. `docs/exec-plans/active/index.md`
9. files in `docs/exec-plans/completed/`

## Delta Interview Checklist

Ask for the delta only:

- what new capability is wanted next
- which users or roles are affected
- what the new v-next scope is
- what is explicitly out of scope for this wave
- which command groups, outputs, or APIs change
- whether any new entities, permissions, integrations, or storage assumptions are introduced
- which unit behaviors must be covered
- which end-to-end flows must be covered
- which commands must pass before the new tasks can promote

## Validation

Before handoff, confirm:

- the updated specs match the next active plans
- required commands still match the generated Makefile or documented command surface
- promotion rules still say that failing required tests block advancement
- the new queue is understandable without external context
