# Bootstrap foundation

```json taskmeta
{
  "id": "010-bootstrap-foundation",
  "title": "Bootstrap foundation",
  "order": 10,
  "status": "active",
  "next_task_on_success": "011-first-vertical-slice",
  "execution_requirements": {
    "worker_sandbox": "workspace-write",
    "evaluator_sandbox": "read-only",
    "network_required": false,
    "blocker_policy": "standard_rca_after_3"
  },
  "prompt_docs": [
    "AGENTS.md",
    "ARCHITECTURE.md",
    "docs/PRODUCT_SENSE.md",
    "docs/CLI_SURFACE.md",
    "docs/PLANS.md"
  ],
  "required_commands": [
    "make verify",
    "make worker-smoke"
  ],
  "required_files": [
    "pyproject.toml",
    "Makefile",
    "scripts/ralph/run-once.sh",
    "docs/exec-plans/active/index.md"
  ],
  "human_review_triggers": [
    "The task broadens into product-specific feature work",
    "The docs and scaffold disagree on the repo contract",
    "The scaffold does not support the documented deterministic commands"
  ]
}
```

## Objective

Bootstrap the repository so it has a coherent docs tree, a minimal Python CLI scaffold, and a working Ralph loop foundation.

## Scope

- generate the baseline docs
- create the predefined Python CLI harness scaffold
- install the Ralph loop
- expose deterministic commands
- expose an operator-visible `make worker-logged` path and documented process log levels

## Out of scope

- advanced product features
- optional integrations
- broad workflow customization beyond the documented preset

## Exit criteria

1. The baseline docs exist.
2. The Python CLI scaffold exists with predefined pytest, Ruff, mypy, and Makefile config.
3. The Ralph scripts exist.
4. `make verify` passes.
5. `make worker-smoke` passes.
6. The repo documents `make worker-logged`, the `logs/` directory, and the supported process log levels for manual verification.

## Required checks

- `make verify`
- `make worker-smoke`

## Evaluator notes

Promote only when the docs, scaffold, and Ralph scripts agree on the same repo contract.
Do not promote if `make verify` fails, even if the bootstrap looks complete by inspection.

## Progress log

- Start here. Append timestamped progress notes as work lands.
