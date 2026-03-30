# Ralph Loop v2

This package upgrades the repository from a repair loop to a task-promotion loop.

## What changed

The first version of the loop could repeatedly work on one prompt, but it could not reliably decide when to advance. This version adds:

- machine-readable task contracts in `docs/exec-plans/active/*.md`
- deterministic checks
- a read-only evaluator pass with structured JSON output
- automatic promotion to the next task when the current task is truly complete
- task-level execution requirements that can switch selected tasks onto a non-default worker sandbox lane
- repeated-blocker tracking that auto-branches the third identical environment-specific blocker into an RCA task
- an explicit manual promotion path for exceptional stalled-but-done cases

## Files

- `scripts/ralph/run-once.sh`: one full worker/evaluator/promotion cycle
- `scripts/ralph/run-loop.sh`: repeated unattended cycles
- `scripts/ralph/status.sh`: inspect current task, latest evaluation, blocker tracker, and backlog
- `scripts/ralph/render-task-prompt.mjs`: build the worker prompt from the current task
- `scripts/ralph/evaluate-task.mjs`: run deterministic checks and a read-only evaluator
- `scripts/ralph/record-blocker.mjs`: normalize and persist repeated blocker signatures
- `scripts/ralph/branch-rca-task.mjs`: auto-create blocker RCA tasks and switch queue priority
- `scripts/ralph/promote-task.mjs`: move a finished task forward
- `scripts/ralph/manual-promote.sh`: manually promote the current task with a recorded reason and optional artifact reference
- `state/current-task.txt`: current task id
- `state/current-cycle.json`: live cycle phase/status for the current run
- `state/evaluation.json`: latest decision
- `state/blocker-tracker.json`: repeat-blocker signature history and RCA branching state
- `state/backlog.md`: rendered queue snapshot
- `state/artifacts/`: per-cycle raw worker/evaluator/commit artifacts

## Logging

- `state/run-log.md` is the compact operator log
- `state/current-cycle.json` shows whether the current run is still active and which phase it is in
- `state/blocker-tracker.json` tracks repeated blocker signatures per task
- full raw output for each cycle is written under `state/artifacts/`
- manual operator runs should use `make worker-logged`, which writes a timestamped worker log under `logs/`
- generated repos should document a process log level environment variable such as `LOG_LEVEL`
- inspect artifact files when the compact log points to a failed phase
- `state/run-log.md` also appends a compact health line after each cycle: `o` for promoted success, `x` for completed non-promotion/failure or RCA auto-branch, and `!` for a stalled worker cycle
- `state/run-log.md` also records the chosen worker/evaluator sandbox for each task cycle

## Recommended usage

### Dry run one cycle

```bash
./scripts/ralph/run-once.sh
./scripts/ralph/status.sh
```

### Run a longer unattended loop

```bash
RALPH_LOOP_SLEEP_SECONDS=45 ./scripts/ralph/run-loop.sh
```

Default sleep is `30` seconds when `RALPH_LOOP_SLEEP_SECONDS` is not set.

### Observe progress

```bash
tail -f state/run-log.md
cat state/last-result.txt
cat state/evaluation.json
cat state/current-cycle.json
ls logs/
tail -f logs/worker-*.log
```

### Manual promotion for stalled-but-done tasks

Use this only when the task is substantively complete but the loop stalled or the latest evaluation is no longer trustworthy.

```bash
./scripts/ralph/manual-promote.sh

./scripts/ralph/manual-promote.sh \
  --reason "task is complete; loop stalled after implementation" \
  --artifact state/artifacts/<cycle-dir>
```

If no reason is supplied, the override records the default reason `operator manual promotion`.

## Operator guidance

- Keep tasks small and vertically sliced.
- Prefer deterministic gates over “try harder” loops, and use evaluator review only when the task contract still needs semantic judgment.
- Do not mix multiple feature fronts into one task.
- `run-once.sh` always rewrites `state/current-cycle.json`, `state/evaluation.json`, `state/backlog.md`, and `state/last-result.txt`; treat those as loop-owned state.
- When a completed task changes shipped features, fixes operator-visible behavior, adds commands, or changes setup/runtime guidance, update `README.md` before considering the task finished.
- if the worker goes silent and `worker.jsonl` stops changing past the stall timeout, the harness marks the cycle as `stalled`, writes a stall artifact, appends `!` to the health line, and stops the unattended loop for operator triage unless that identical stall has already repeated enough times to auto-branch into RCA
- a single `!` does not automatically mean “create the RCA task now”; the loop records the blocker signature first and only auto-branches into the RCA/fix plan after the same blocker repeats enough times to satisfy the environment-blocker rule
- when a repeated blocker hits the threshold, the loop auto-generates a blocker-specific RCA task, marks the original task as blocked, switches `state/current-task.txt` to the RCA task, and restores the original task when the RCA task promotes
- if a task declares live network access in `taskmeta.execution_requirements`, `run-once.sh` switches the worker to the declared sandbox lane instead of always using `workspace-write`
- if evaluation ends in `blocked`, `run-loop.sh` stops for operator triage instead of blindly retrying the same runtime constraint forever
- Required commands come from each task doc’s `taskmeta.required_commands`; `evaluate-task.mjs` runs exactly those commands plus required-file checks.
- `manual-promote.sh` is an explicit operator override; use it only for exceptional stalled-but-done cases. If you omit `--reason`, it records `operator manual promotion`.
- If the evaluator repeatedly returns `not_done`, tighten the active task doc instead of making the prompt larger.
- If a task is semantically done but not promotable, fix the contract or the deterministic checks; if you must override, use `manual-promote.sh` so the reason is recorded instead of silently skipping ahead.
