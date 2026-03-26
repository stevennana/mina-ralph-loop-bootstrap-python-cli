# Doc Baseline

Generate this baseline before treating the Ralph loop as installed.

## Root files

- `AGENTS.md`
  - short map, read order, guardrails, current environment assumptions
- `ARCHITECTURE.md`
  - top-level domains, layering, boundaries, runtime shape

## `docs/`

- `docs/PRODUCT_SENSE.md`
  - product definition, user, problem, principles, non-goals
- `docs/CLI_SURFACE.md`
  - command groups, operator-visible flows, CLI output/input expectations, and UX constraints
- `docs/PLANS.md`
  - execution-plan philosophy, promotion rules, and required-check usage
- `docs/DESIGN.md`
  - high-level design/system framing if the project needs a cross-cutting design narrative
- `docs/QUALITY_SCORE.md`
  - domain/layer quality grades, verification posture, and immediate priorities
- `docs/RELIABILITY.md`
  - reliability expectations, failure modes, verification, runtime startup, operator logging, and test strategy
- `docs/SECURITY.md`
  - security expectations, secrets, public/private surfaces, validation boundaries

## `docs/design-docs/`

- `index.md`
- `core-beliefs.md`
- at least one project-specific design doc

## `docs/product-specs/`

- `index.md`
- at least one project-specific product spec
- if more than one feature front is in scope, create one spec per major feature instead of collapsing them into one generic flow doc

## `docs/exec-plans/`

- `active/index.md`
- at least one active task contract with `taskmeta`
- `tech-debt-tracker.md`
- create `completed/` even if empty
- if the product has multiple major features, the initial queue should contain multiple small feature-sliced tasks rather than a single omnibus “first slice”
- supporting architecture/design/product docs should be detailed enough that each plan page can be written without guessing

## `docs/generated/`

- create the directory
- include placeholder/generated artifacts only when the scaffold already has them

## `docs/references/`

Create local references when they materially help the agent.
Examples:

- framework and library references
- CLI contract notes
- provider request/response shapes
- process supervision or logging contracts

If the user provides local or online references, analyze them into `docs/references/` and keep the useful project-specific information in-repo for future implementation and later feature waves.

## Stop Condition

Do not move on to scaffold creation until:

- the founder-facing product intent is captured
- the repo read order is clear
- the initial task queue exists
- the deterministic commands can be named in advance
- unit, integration, and CLI E2E expectations are written into docs and task contracts
- promotion-blocking command gates are written into docs and task contracts
