# Ralph Loop Task Queue

This queue is the task-level promotion source of truth for {{PROJECT_NAME}}.

Only task files in this directory that contain a `taskmeta` JSON block are eligible for automatic selection, evaluation, and promotion.
Queue depth may legitimately exceed five tasks when the planner was asked for smaller slices or a longer backlog.

## Current recommended sequence
{{TASK_SEQUENCE_NUMBERED}}

## Operating rule

A task may be promoted only when all of the following are true:

- deterministic checks pass
- the evaluator marks the task as `done`
- the evaluator recommends promotion
- the task metadata declares a `next_task_on_success`, or explicitly declares that the queue ends here

## When this queue ends

When the active sequence is exhausted, do not continue with ad hoc prompts alone.
Update the relevant product specs and design docs first, then seed the next active queue for the next feature wave.
