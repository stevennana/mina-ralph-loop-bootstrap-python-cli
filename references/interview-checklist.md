# Interview Checklist

Use this checklist to decide whether the user's answers are complete enough to write the docs and queue without guessing.
Pick the interview lane first instead of treating every repo like a fresh v1 bootstrap.
Preferred interaction style: before the first substantive product question, first handle companion-skill guidance and resolve the install decision, then review the product/reference context, then in a separate prompt recommend `Plan` mode if the user wants selectable option lists, then in a separate prompt tell the user to say `continue` when ready; after that, ask one question at a time, give suggested options when useful, and always allow a free-form answer.
Before the first substantive product question, check whether the pinned companion skill set is installed and, if the user allows it, summarize the missing companion skill, ask whether to auto-install it before product analysis and documentation starts, use the helper installer flow by default, and then handle that install before the interview.
Keep the printed manual commands aligned with the actual upstream repo paths.

## Choose The Interview Lane

Use the full bootstrap checklist only when the repo is empty, nearly empty, or still lacks a stable product definition and docs baseline.
If the repo already has code and the current v1 scope, goals, and baseline docs are explicit enough to build on, do not restart discovery from scratch. Treat it as a continuation run and ask for the delta only.
If the repo has code but the current docs are too weak to tell what v1 already is, first inspect the repo and existing docs, then ask only the minimum recovery questions needed to restate the current product before defining the next wave.

For continuation runs, combine this checklist with `references/expansion-mode.md`.
The stop condition is docs and queue refresh, not immediate implementation.

## Full Bootstrap Checklist

Use this when defining a fresh v1 or when the current repo is too underspecified to recover intent from existing materials.

### Identity

- project name
- one-line product definition
- primary user
- why this product exists

### Scope

- v1 goals
- explicit non-goals
- what must be demoable in v1
- which distinct feature fronts should each become their own spec or task slice

### Domain Model

- primary entities
- ownership rules
- key relationships

### Operator-Visible Shape

- command groups
- core CLI flows
- required read-only or admin surfaces
- what absolutely must be test-covered end-to-end
- which external-resource flows must be test-covered end-to-end before promotion

### Technical Basis

- storage/runtime assumptions
- external dependencies or APIs
- secrets/config shape
- single-user vs multi-user expectations
- whether any feature depends on outside resources such as AI or third-party services

### Quality Bar

- deterministic commands
- unit-test expectations
- integration-test expectations if any
- required CLI E2E flows
- explicit E2E coverage for external-resource features before promotion
- promotion-blocking test gates
- what `make verify` is expected to prove
- reliability or security caveats that must be documented

### Ralph Loop Readiness

- initial task queue sequencing
- first vertical slice
- hardening/maintenance task
- operator expectations for `run-once` and unattended loop runs
- confirmation that failing required tests prevent promotion

### Stop Asking When

You can clearly write:

- `AGENTS.md`
- `ARCHITECTURE.md`
- the top-level docs
- at least one design doc
- at least one product spec
- a clear feature map for how many product specs and active tasks should be created
- an initial active task queue with deterministic checks
- a concrete test strategy with explicit promotion-blocking commands

If any of those still requires guessing, keep asking.

## Continuation Checklist

Use this when the repo already has a defined v1, an existing docs tree, or meaningful implementation that the next wave must build on.
Do not re-ask the bootstrap questions unless the existing product definition is missing, contradictory, or intentionally being reset.

### Existing Baseline To Confirm

- what the repo already does today
- which current docs and completed plans define the existing v1
- whether the existing scope/goals/non-goals remain valid or need a targeted correction
- whether any current commands, harness rules, or promotion gates are already part of the operator contract

### Next-Wave Delta

- what new capability is wanted next
- which users or roles are affected
- what this wave is trying to achieve beyond the current v1
- what is explicitly out of scope for this wave
- which current command groups, outputs, APIs, entities, or jobs change
- whether any new entities, permissions, integrations, or storage assumptions are introduced

### Verification Delta

- which new or changed unit behaviors must be covered
- which CLI end-to-end flows must be added or revised
- which external-resource flows need end-to-end proof before promotion
- which deterministic commands must pass before the new tasks can promote
- whether `make verify` or other gates need to expand for this wave

### Queue Delta

- which new or revised product specs are needed
- whether existing design docs need updates before planning
- how the next active task wave should be sliced
- what the first next-wave vertical slice is
- whether any blocker, RCA, or hardening task must precede feature work

### Stop Asking When

You can clearly write:

- an updated or new product spec for the next feature wave
- any needed design-doc or architecture-doc changes
- a new active queue sequence with explicit `taskmeta`
- promotion-blocking checks for each new task
- any required updates to harness/operator docs caused by the new wave

If any of those still requires guessing, keep asking.
