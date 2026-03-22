# Environment Blockers

Use this reference when a task is blocked by the current runner, sandbox, wrapper path, or operator environment rather than by normal product implementation work.

## Core Rule

Do not let the same environment-specific blocker keep a task spinning indefinitely.

If a similar blocker appears three times for the same task, treat it as its own problem to investigate and fix.

## Recognizing The Pattern

This is an environment blocker when:

- the product behavior appears complete in substance
- the same deterministic failure keeps repeating
- the failure depends on how the command is launched, wrapped, sandboxed, or hosted
- the remaining gap is not ordinary feature work
- the worker phase stops making forward progress even though the loop still thinks it is running

## Worker Stall Detection

The harness should not try to prove Codex internal health directly.

Instead, generated Ralph loops should treat changes to `worker.jsonl` as the worker heartbeat.

If the worker phase stays active but `worker.jsonl` stops changing for longer than the configured stall timeout:

- classify the cycle as stalled
- stop the worker
- preserve a stall artifact with timing evidence
- stop the unattended loop instead of retrying blindly
- hand the task to operator triage before deciding whether this is a transient issue, a completed-but-stalled case, or a repeated blocker that now needs RCA

A single stall does not automatically mean “create the RCA task now.”
It means “stop safely, preserve evidence, and triage.”

## Exceptional Path

When a similar environment-specific blocker occurs three times for the same active task:

1. stop retrying the same task unchanged
2. write a short RCA summary into the current task log and debt tracking
3. create a small exec-plan specifically for the blocker investigation/fix
4. make that RCA/fix plan the current priority
5. once the blocker plan is completed, return to the original task

## RCA / Fix Plan Requirements

The blocker-specific plan should:

- describe the repeated failure precisely
- separate repo bugs from environment constraints
- name the exact failing command and launch shape
- define the smallest fix or validation needed
- define what evidence is required before returning to the original task

## Return Path

After the blocker-specific plan is done:

- restore the original task as current
- keep the RCA task in completed history
- update the original task log with the blocker resolution
