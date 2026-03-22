# RELIABILITY.md

## Purpose
Define the reliability expectations and failure-handling rules for {{PROJECT_NAME}}.

## Core Reliability Rules
{{RELIABILITY_RULES_BULLETS}}

## Verification
{{RELIABILITY_VERIFICATION_BULLETS}}

## Runtime Startup Contract
If the app depends on persistent runtime state, document how runtime preparation happens and how `make worker-smoke` proves the real worker path actually works.

## Operator Logging
Document how `make worker-logged` writes operator-visible logs into `logs/`, which environment variable controls the log level, and which levels are supported for manual debugging.

## Test Strategy
Document which behaviors are protected by unit tests, which flows require integration or CLI E2E coverage, and which command failures block task promotion.
