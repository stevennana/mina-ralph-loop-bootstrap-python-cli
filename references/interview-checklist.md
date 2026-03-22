# Interview Checklist

Use this checklist to decide whether the user's answers are complete enough to write the baseline docs.

## Identity

- project name
- one-line product definition
- primary user
- why this product exists

## Scope

- v1 goals
- explicit non-goals
- what must be demoable in v1
- which distinct feature fronts should each become their own spec or task slice

## Domain model

- primary entities
- ownership rules
- key relationships

## Operator-visible shape

- command groups
- primary CLI flows
- required read-only or admin surfaces
- what absolutely must be test-covered end-to-end
- which external-resource flows must be test-covered end-to-end before promotion

## Technical basis

- storage/runtime assumptions
- external dependencies or APIs
- secrets/config shape
- single-user vs multi-user expectations
- whether any feature depends on outside resources such as AI or third-party services

## Quality bar

- deterministic commands
- unit-test expectations
- integration-test expectations if any
- required CLI E2E flows
- explicit E2E coverage for external-resource features before promotion
- promotion-blocking test gates
- what `make verify` is expected to prove
- reliability or security caveats that must be documented

## Ralph loop readiness

- initial task queue sequencing
- first vertical slice
- hardening/maintenance task
- operator expectations for `run-once` and unattended loop runs
- confirmation that failing required tests prevent promotion

## Stop Asking When

You can clearly write:

- `AGENTS.md`
- `ARCHITECTURE.md`
- the top-level docs
- at least one design doc
- at least one product spec
- a clear feature map for how many product specs and active tasks should be created
- an initial active task queue with deterministic checks
- a concrete test strategy with explicit promotion-blocking commands
