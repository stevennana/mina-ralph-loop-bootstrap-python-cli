# Ralph Loop v2

This package upgrades the repository from a repair loop to a task-promotion loop.

## What changed

The loop now adds:

- machine-readable task contracts in `docs/exec-plans/active/*.md`
- deterministic checks
- a read-only evaluator pass with structured JSON output
- automatic promotion to the next task when the current task is truly complete

## Files

- `scripts/ralph/run-once.sh`: one full worker/evaluator/promotion cycle
- `scripts/ralph/run-loop.sh`: repeated unattended cycles
- `scripts/ralph/status.sh`: inspect current task, latest evaluation, and backlog
- `scripts/ralph/render-task-prompt.mjs`: build the worker prompt from the current task
- `scripts/ralph/evaluate-task.mjs`: run deterministic checks and a read-only evaluator
- `scripts/ralph/promote-task.mjs`: move a finished task forward
- `state/current-task.txt`: current task id
- `state/current-cycle.json`: live cycle phase/status for the current run
- `state/evaluation.json`: latest decision
- `state/backlog.md`: rendered queue snapshot
- `state/artifacts/`: per-cycle raw worker/evaluator/commit artifacts

## Logging

- `state/run-log.md` is the compact operator log
- `state/current-cycle.json` shows whether the current run is still active and which phase it is in
- full raw output for each cycle is written under `state/artifacts/`
- manual operator runs should use `make worker-logged`, which writes a timestamped worker log under `logs/`
- generated repos should document a process log level environment variable such as `LOG_LEVEL`
- `state/run-log.md` also appends a compact health line after each cycle: `o` for promoted success, `x` for completed non-promotion/failure, and `!` for stalled worker triage stop

## Recommended usage

```bash
./scripts/ralph/run-once.sh
./scripts/ralph/status.sh
```

```bash
RALPH_LOOP_SLEEP_SECONDS=45 ./scripts/ralph/run-loop.sh
```

## Operator guidance

- Keep tasks small and vertically sliced.
- Prefer deterministic gates plus evaluator review over “try harder” loops.
- `run-once.sh` always rewrites loop-owned state files; treat them as harness state.
- if the worker goes silent and `worker.jsonl` stops changing past the stall timeout, the harness marks the cycle as `stalled`, writes a stall artifact, appends `!` to the health line, and stops the unattended loop for operator triage
- a single `!` does not automatically mean “create the RCA task now”; only repeated environment-specific blockers on the same task should branch into the RCA/fix exec-plan flow
- Required commands come from each task doc’s `taskmeta.required_commands`; `evaluate-task.mjs` runs exactly those commands plus required-file checks.
