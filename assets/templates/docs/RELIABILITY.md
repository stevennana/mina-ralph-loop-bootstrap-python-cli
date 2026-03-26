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
When tests cover subtle or business-critical behavior, capture why those tests exist so future loops do not weaken them casually.
If a user-visible behavior depends on an outside resource such as AI or a third-party service, require CLI E2E coverage before promotion.

## Known Gaps
Document any reliability gaps, operational caveats, or deferred safeguards directly in this file instead of leaving them implicit.

## Environment-Specific Verification Blockers
If the direct operator path passes but the current sandboxed or wrapped runner still fails, record that separately from normal product bugs and escalate it explicitly instead of hiding it inside generic “not done” wording.
