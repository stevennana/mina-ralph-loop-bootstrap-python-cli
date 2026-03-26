# CLI_SURFACE.md

## Goal
Describe the operator-facing command surface of {{PROJECT_NAME}} so an agent can implement the CLI without guessing the workflow model.

## Tech Direction
- Python CLI application
- Typer-based command tree
- rich terminal output where useful
- worker/runtime commands for unattended operation

## Command Groups
{{COMMAND_GROUPS_MARKDOWN}}

## Primary Flows
{{PRIMARY_FLOWS_MARKDOWN}}

## CLI Rules
{{CLI_RULES_BULLETS}}

## Operator Notes
{{SURFACE_NOTES_BULLETS}}

## CLI Non-Goals for v1
{{CLI_NON_GOALS_BULLETS}}
