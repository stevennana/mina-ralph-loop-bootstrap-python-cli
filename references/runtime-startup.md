# Runtime Startup Contract

Use this reference when the generated repo has persistent runtime state such as a database, local durable storage, migrations, or queue state.

## Core Rule

Do not treat lint, typecheck, or tests as proof that the shipped runtime can actually start.

If the app depends on runtime preparation, the repo should expose deterministic commands that prove:

- the runtime state is prepared
- the production-style worker can boot successfully
- the worker can process a minimal scoped action and exit cleanly

## Required Pattern

For repos with persistent runtime state, add:

- `make worker-smoke`
- `make worker-logged` when humans need to inspect real process behavior directly

## Acceptance Rule

Do not consider the harness ready until either:

- `make verify` includes the runtime startup proof, or
- the active task contract explicitly requires `make worker-smoke` alongside `make verify`
