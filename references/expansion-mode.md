# Expansion Mode

Use this reference when the repository already has the baseline docs, scaffold, and Ralph loop, but the current queue is complete and the founder wants the next wave of work defined.

## Goal

Extend the same repo and the same skill workflow without creating a separate planning process.

The sequence stays:

1. understand what is already implemented
2. interview for the next feature wave
3. update docs first
4. create the next active exec-plans
5. validate the queue and command contract
6. stop there and hand back the refreshed queue

## When To Use Expansion Mode

Use expansion mode when most or all of these are true:

- the baseline docs already exist
- `scripts/ralph/` already exists
- the initial queue is completed or nearly completed
- the founder wants additional product capability, not just bug fixes inside the current plans

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

Before proposing new work, search the current codebase for existing implementations and partial attempts.
Do not create a fresh implementation plan for something that already exists under a different name or location.

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

## Stop Condition

You can stop asking questions when you can clearly write:

- an updated or new product spec for the next feature wave
- any needed design-doc changes
- a new active queue sequence with explicit `taskmeta`
- promotion-blocking checks for each new task

If any of those still requires guessing, keep asking.

## Queue Refresh Rules

- Keep completed plans in `docs/exec-plans/completed/` as history.
- Do not silently rewrite history to make the queue look cleaner.
- Update `docs/exec-plans/active/index.md` so the next wave order is obvious.
- Prefer small vertical slices over one large omnibus plan, and size the queue to the requested backlog depth.
- When the founder does not specify queue depth, default to `SLICE_SIZE=balanced` and `BACKLOG_DEPTH=10-15 tasks`.
- Allow multiple exec-plans to reference the same product spec when that is the clearest way to keep tasks narrow.
- Include at least one user-visible or operator-visible slice in the new wave unless the founder explicitly wants infrastructure-only follow-up.
- Refresh `docs/PLANS.md`, `docs/RELIABILITY.md`, and other harness-engineering docs if the new wave changes the operator contract.
- Treat the expansion-run deliverable as docs and exec-plans only; do not start implementation in the same pass.

## Stop Boundary

After the docs and next active queue are refreshed:

- stop and hand the repo back
- do not modify application code, package scripts, schemas, tests, or runtime wiring in the same continuation run
- let Ralph or a later explicit implementation request pick up one active task afterward

## Validation

Before handoff, confirm:

- the updated specs match the next active plans
- required commands still match the generated Makefile or documented command surface
- promotion rules still say that failing required tests block advancement
- the new queue is understandable without external context
- the proposed next wave is based on what the repo already contains, not on missing-code assumptions
