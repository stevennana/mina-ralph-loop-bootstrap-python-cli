# First vertical slice

```json taskmeta
{
  "id": "011-first-vertical-slice",
  "title": "First vertical slice",
  "order": 11,
  "status": "queued",
  "next_task_on_success": "012-hardening-and-maintenance",
  "prompt_docs": [
    "AGENTS.md",
    "ARCHITECTURE.md",
    "docs/PRODUCT_SENSE.md",
    "docs/CLI_SURFACE.md",
    "docs/product-specs/core-flow.md"
  ],
  "required_commands": [
    "make verify"
  ],
  "required_files": [
    "{{FIRST_VERTICAL_SLICE_FILE_HINT}}"
  ],
  "human_review_triggers": [
    "The slice is not actually operator-visible",
    "The task mixes multiple feature fronts",
    "The deterministic checks do not prove the claimed behavior"
  ]
}
```

## Objective

Implement the first operator-visible vertical slice for {{PROJECT_NAME}}.

## Scope

{{FIRST_VERTICAL_SLICE_SCOPE_BULLETS}}

## Out of scope

{{FIRST_VERTICAL_SLICE_NON_GOALS_BULLETS}}

## Exit criteria

{{FIRST_VERTICAL_SLICE_EXIT_CRITERIA_NUMBERED}}

## Required checks

- `make verify`

## Evaluator notes

Promote only when the slice works end-to-end in substance, not just in isolated helpers.
Do not promote if `make verify` fails, even if the slice appears functionally complete.

## Progress log

- Start here. Append timestamped progress notes as work lands.
