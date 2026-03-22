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

## When To Loop

If the docs are still rough:

- improve `ARCHITECTURE.md`, `docs/CLI_SURFACE.md`, `docs/design-docs/*`, or `docs/product-specs/*` first
- then regenerate or rewrite the exec-plan pages
- then review each exec-plan page again
