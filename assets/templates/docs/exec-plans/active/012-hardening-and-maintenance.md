# Hardening and maintenance

```json taskmeta
{
  "id": "012-hardening-and-maintenance",
  "title": "Hardening and maintenance",
  "order": 12,
  "status": "queued",
  "next_task_on_success": null,
  "prompt_docs": [
    "AGENTS.md",
    "ARCHITECTURE.md",
    "docs/QUALITY_SCORE.md",
    "docs/RELIABILITY.md",
    "docs/SECURITY.md"
  ],
  "required_commands": [
    "make verify",
    "make worker-smoke"
  ],
  "required_files": [
    "scripts/ralph/README.md"
  ],
  "human_review_triggers": [
    "The task expands into broad feature work",
    "Reliability or security docs do not match the actual code",
    "Loop scripts mutate unrelated repo state without clear reason",
    "The same environment-specific verification blocker has repeated three times and now needs its own RCA/fix plan"
  ]
}
```

## Objective

Close the gap between the implemented slice and the repository's reliability, security, and automation posture.

## Scope

- reconcile docs and implementation drift
- keep the deterministic checks healthy
- tighten operator guidance for the Ralph loop
- ensure the loop can detect and surface stalled worker cycles instead of waiting forever
- keep operator-visible worker logging aligned with the actual startup path
- record remaining debt explicitly

## Out of scope

- major new product features
- unrelated infrastructure expansion

## Exit criteria

1. `make verify` passes.
2. `make worker-smoke` passes when the repo depends on persistent runtime state.
3. Loop documentation matches the actual scripts.
4. Reliability/security docs reflect the current implementation.
5. Operator-visible startup logging and log-level guidance match the actual worker behavior.
6. Remaining debt is explicit.

## Required checks

- `make verify`
- `make worker-smoke`

## Evaluator notes

Promote only when the repository is ready for longer unattended Ralph-loop runs under the current task contract.
Do not promote if `make verify` fails, even if the hardening changes look correct by inspection.

## Progress log

- Start here. Append timestamped progress notes as work lands.
