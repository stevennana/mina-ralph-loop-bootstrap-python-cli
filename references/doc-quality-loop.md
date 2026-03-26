# Doc Quality Loop

Use this reference after drafting or revising repository docs and exec-plan pages.

## Goal

Do not stop at “the file exists.” Keep revising until each important doc is decision-complete enough that an implementer can act without guessing.

## Review Order

When preparing exec-plans, review the related docs in this order:

1. `docs/PRODUCT_SENSE.md`
2. `docs/CLI_SURFACE.md`
3. `ARCHITECTURE.md`
4. relevant files in `docs/design-docs/`
5. relevant files in `docs/product-specs/`
6. only then the target file in `docs/exec-plans/active/`

## Quality Questions For Every Doc

For each doc, ask:

- is the scope concrete instead of thematic
- are the terms and entities consistent with the rest of the repo
- are the command groups, surfaces, and behaviors specific enough to implement
- are constraints, non-goals, and failure boundaries explicit
- are tests and promotion gates clear
- would an implementer still need to invent key behavior

If any answer is weak, revise the supporting docs before finalizing the plan.

## Exec-Plan Quality Questions

Each exec-plan page should be reviewed on its own before handoff.

Check that it has:

- one narrow feature slice, not a theme or roadmap chunk
- a concrete objective
- explicit out-of-scope boundaries
- exit criteria that prove the feature, not the whole product
- required checks that match the behavior
- enough description that the implementer does not need to infer missing behavior from other docs alone

## When To Loop

If the docs are still rough:

- improve `ARCHITECTURE.md`, `docs/CLI_SURFACE.md`, `docs/design-docs/*`, or `docs/product-specs/*` first
- then regenerate or rewrite the exec-plan pages
- then review each exec-plan page again

Repeat until the docs and plans are sufficiently detailed.

## When To Return To Interview

If the quality problem comes from missing product intent rather than weak writing:

- stop generating more guidance
- go back to the interview stage
- ask only the missing questions needed to remove the ambiguity

## When To Branch Into RCA

If the blocker is neither doc quality nor missing intent, but a repeated environment-specific failure:

- stop the repeated attempt loop
- create a separate RCA/fix exec-plan for that blocker
- resolve that blocker first
- then return to the original task
