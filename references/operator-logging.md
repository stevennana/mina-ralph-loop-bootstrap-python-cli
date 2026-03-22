# Operator Logging Contract

Use this reference when the generated repo needs operator-visible process logs outside the test harness.

## Core Rule

Do not make the production-style worker path observable only through transient terminal output.

Generated repos should give operators a stable way to:

- start the long-running worker with logs persisted to disk
- choose a process log level for manual debugging
- inspect the latest worker log without relying on Ralph artifacts

## Required Pattern

Generated repos should expose:

- `make worker-logged`
- a `logs/` directory for operator-visible process logs
- a log level environment variable such as `LOG_LEVEL`

## What `make worker-logged` Should Do

The logged startup path should:

- start the same long-running worker used in real operation
- create a timestamped log file under `logs/`
- capture stdout and stderr into that log file
- print the log file path so the operator can tail it immediately
