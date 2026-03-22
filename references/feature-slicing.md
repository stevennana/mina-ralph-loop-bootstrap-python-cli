# Feature Slicing

Use this reference when turning founder answers into product specs and executable task contracts.

## Core Rule

Do not collapse multiple user-visible or operator-visible features into one “first slice” unless the product truly has only one behavior front.

Each distinct feature area should normally get:

- its own product spec under `docs/product-specs/`
- one or more small executable tasks under `docs/exec-plans/active/`
- in the initial queue, at least one executable task that maps cleanly to that spec

## What Counts As A Distinct Feature

Treat these as separate feature fronts unless there is a strong reason to combine them:

- project initialization and config setup
- task creation or editing
- queue listing and filtering
- promotion or state transitions
- worker execution
- status and inspection surfaces
- external provider integrations

## External Resource Rule

If a feature depends on an outside resource such as AI, email, or a third-party API:

- keep that feature in its own spec or task unless the dependency is trivial
- require its relevant CLI E2E scenario before promotion
