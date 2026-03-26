# Feature Slicing

Use this reference when turning founder answers into product specs and executable task contracts.

## Core Rule

Do not collapse multiple user-visible or operator-visible features into one “first slice” unless the product truly has only one behavior front.

Each distinct feature area should normally get:

- its own product spec under `docs/product-specs/`
- one or more small executable tasks under `docs/exec-plans/active/`
- in the initial queue, at least one executable task that maps cleanly to that spec
- its exec-plan page written only after the related architecture/design/product docs are reviewed and tightened
- additional exec-plan pages for the same spec whenever the selected slice-size or backlog-depth target would otherwise force one oversized task

## What Counts As A Distinct Feature

Treat these as separate feature fronts unless there is a strong reason to combine them:

- project initialization and config setup
- task creation or editing
- queue listing and filtering
- promotion or state transitions
- worker execution
- status and inspection surfaces
- external provider integrations

## Task Sizing Rule

One task should cover at most:

- one operator-visible or user-visible feature slice
- plus the smallest enabling work required to make that slice real

Do not create a task that mixes several independent feature areas just because they all belong to “v1”.

## Minimum Mapping Rule

Before writing executable tasks, create or update the feature-spec list.

If the repo has multiple in-scope feature fronts:

- the product-specs index should list them explicitly
- the active queue should sequence them explicitly
- the first executable task should not try to finish all of them at once
- each non-hardening executable task should usually point at exactly one product spec
- a product spec may legitimately map to multiple executable tasks when that keeps the slices narrow
- each exec-plan page should be reviewed individually before handoff

## External Resource Rule

If a feature depends on an outside resource such as AI, email, or a third-party API:

- keep that feature in its own spec or task unless the dependency is trivial
- require its relevant CLI E2E scenario before promotion

## Smell Checks

Your slicing is probably too broad if any one task:

- changes multiple major command groups or feature areas
- requires more than one product spec to understand its success condition
- has exit criteria that read like a mini-roadmap
- mixes auth/integration work with core workflow features and reporting
- references multiple product-spec docs in one executable contract
- reads like a broad milestone instead of a task one agent can finish safely
