---
name: mina-rich-cli-interface
description: Use when a Mina-bootstrapped Python CLI repository needs a Rich-based terminal interface, including Tables, Panels, Progress, Live updates, Rich logging, tracebacks, and stable operator-facing output under a Typer CLI.
---

# Mina Rich CLI Interface

This skill is inspired by the Rich documentation, the Rich GitHub repository, and `rich-cli`, but adapted to the Mina Python CLI bootstrap contract.

Use this skill when a Mina-generated Python CLI repo needs deliberate Rich-powered terminal UX instead of plain text output alone.

## Assumptions

- the repo uses `uv`
- the CLI surface is built with Typer
- `pyproject.toml` owns runtime dependencies
- when a Rich CLI interface is chosen, `rich` is an essential runtime dependency
- CLI E2E tests may need stable output assertions even when Rich is used

## Workflow

1. Read the current CLI docs, command flows, and operator-visible outputs first.
2. Decide which surfaces should remain plain/stable and which benefit from Rich formatting.
3. Confirm `rich` is present in runtime dependencies before implementing Rich UI behavior.
4. Shape output around operator tasks using the smallest Rich primitive that helps.
5. Update docs and CLI E2E coverage when Rich changes visible command behavior.

## Rich CLI / Command-Line UI Design Guidelines

Use this guidance when designing or improving a Python command-line interface, especially when the project uses `rich`, `typer`, `click`, or related terminal UI tools.

### Goal

Design CLI interfaces that are:

- easy for humans to read
- safe for automation and scripting
- consistent across Linux and macOS
- resilient in non-interactive environments
- accessible even when color or advanced terminal features are unavailable

### Core Principles

#### 1. Prefer clarity over decoration

Use visual styling to improve comprehension, not to show off terminal capabilities. A good CLI should still make sense when colors, borders, and animations are removed.

#### 2. Separate human output from machine output

Default output may be optimized for humans, but the tool should also support machine-friendly modes such as:

- `--json`
- `--plain`
- `--quiet`

Keep structured data on `stdout`. Send logs, warnings, and diagnostic messages to `stderr`. Always use proper exit codes.

#### 3. Detect terminal capabilities

Only enable rich formatting when appropriate. Check for:

- TTY vs non-TTY
- terminal width
- color support
- `NO_COLOR`
- `TERM=dumb`

Gracefully degrade when the environment does not support advanced rendering.

#### 4. Color must not be the only signal

Never rely on color alone to communicate meaning. Pair color with text labels, symbols, or structure.

Good:

- `ERROR` in red
- `WARNING` in yellow
- `SUCCESS` in green

Bad:

- red text with no label
- green-only status indicators

#### 5. Help and errors are part of the UI

Help text should be short, direct, and example-driven. Error messages should explain:

- what failed
- why it failed
- what the user can do next

Prefer:

- actionable messages
- suggested fixes
- command examples
- likely typo corrections

Avoid exposing raw stack traces unless the user explicitly requests verbose/debug mode.

#### 6. Interactive prompts must be optional

Interactive prompts are useful, but they must never be required for automation. Anything that can be entered interactively should also be possible through:

- flags
- environment variables
- standard input
- config files

Support flags like:

- `--yes`
- `--force`
- `--dry-run`
- `--no-input`

#### 7. Use progress indicators honestly

Use a progress bar only when progress can be estimated. Use a spinner or indeterminate indicator when the total is unknown.

Do not show fake precision. Do not animate aggressively for long-running background work. Keep refresh rates reasonable.

#### 8. Keep layouts stable

Avoid output that jumps around or reflows unnecessarily. A stable layout is easier to scan and easier to debug.

Use:

- tables for comparison
- panels for grouped summaries
- sections with clear headings
- consistent spacing

Avoid deeply nested boxes, excessive borders, or crowded dashboards.

#### 9. Design for narrow terminals first

Many users work in split panes, SSH sessions, CI logs, or small terminal windows. Assume constrained width.

Prefer:

- short labels
- truncation with clear rules
- compact summaries
- optional expanded detail views

#### 10. Accessibility matters

Ensure the CLI remains usable:

- without color
- with limited contrast
- in screen-reader-like workflows
- when copied into logs or issue reports

Use plain language, consistent terminology, and predictable structure.

## Recommended Output Behavior

### Standard output

Use `stdout` for:

- main results
- tables
- JSON output
- final success summaries

### Standard error

Use `stderr` for:

- warnings
- validation issues
- progress messages when appropriate
- logs
- failures

### Exit codes

Use clear exit codes:

- `0` for success
- non-zero for failures
- distinct codes when meaningful

## Preferred Rich Primitives

- `Console` for structured status and styled text
- `Table` for dense, scan-friendly listings
- `Panel` for summaries and scoped status blocks
- `Progress` for long-running feedback
- `Live` only when live-updating output is genuinely useful
- Rich logging and Rich tracebacks for debugging and operator diagnostics

## Rich-Specific Guidance

### Use Rich when it improves readability

Good use cases:

- status panels
- compact summaries
- readable tracebacks in debug mode
- progress bars
- comparison tables
- syntax-highlighted previews when truly helpful

Do not use Rich just because it is available.

### Prefer semantic styling

Use a small, consistent visual vocabulary. Example:

- bold for headings
- dim for secondary metadata
- yellow for caution
- red for failure
- green for success
- cyan or blue for neutral emphasis

Avoid rainbow-colored output or too many competing styles.

### Panels and tables

Use panels for:

- summaries
- grouped status
- next steps

Use tables for:

- aligned comparisons
- file lists
- command results
- service status views

Do not put long paragraphs inside dense tables.

### Live rendering

Use `Live` views only when the user benefits from real-time updates. Avoid live layouts for simple commands that finish quickly.

## Typer / Click Command Design Guidance

### Keep commands predictable

Prefer simple verb-based command structures, such as:

- `tool init`
- `tool check`
- `tool test`
- `tool status`
- `tool logs`
- `tool deploy`

### Make defaults safe

The default behavior should be the least surprising and least destructive option.

### Use names that match user intent

Flags and subcommands should sound like real user tasks, not internal implementation details.

Good:

- `--output json`
- `--service-name`
- `--follow`
- `--timeout`

Bad:

- `--mode-x`
- `--enable-v2-flow`
- `--internal-format`

### Help text

Each command should include:

- one-line purpose
- key options
- one or two examples

## Python CLI Best Practices

### Testing

CLI behavior should be tested with `pytest`, including:

- exit codes
- help output
- invalid input
- JSON/plain output modes
- non-TTY behavior
- error formatting
- service-related commands

### Configuration

Support configuration through a clear precedence model, for example:

1. CLI flags
2. environment variables
3. config file
4. defaults

Make this precedence explicit in the help or docs.

### Logging

Separate user-facing output from developer/debug logging. Provide:

- normal mode
- verbose mode
- debug mode

### Tracebacks

Hide full tracebacks by default. Show friendly errors unless the user enables `--debug`.

## Linux and macOS Service-Oriented CLI Guidance

When the CLI interacts with system services, launch agents, or daemons:

### Use task-oriented commands

Prefer commands like:

- `install`
- `uninstall`
- `start`
- `stop`
- `restart`
- `status`
- `logs`

### Show platform-aware guidance

On Linux, account for `systemd`. On macOS, account for `launchd`.

Do not assume both platforms behave the same way. Explain platform-specific differences clearly.

### Make status output actionable

A status command should answer:

- is the service installed?
- is it running?
- where are logs?
- what should the user do next?

### Do not hide system command failures

When wrapping system tools, summarize the failure clearly and show the exact command or next step when useful.

## Good UX Patterns

### Good

- clean summaries
- one obvious next step
- compact default output
- verbose details only when requested
- consistent command naming
- predictable flags
- graceful non-TTY fallback

### Bad

- flashy output with poor readability
- color-only meaning
- mandatory prompts
- excessive animation
- unstable layouts
- huge stack traces for normal user mistakes
- mixing logs with machine-readable output

## Default Design Checklist

Before finalizing a CLI UI, verify:

- Is the output readable without color?
- Does it work in a non-TTY environment?
- Can the command be automated without prompts?
- Are errors actionable?
- Is machine-readable output available where needed?
- Is the layout still usable in a narrow terminal?
- Are success, warning, and failure states visually consistent?
- Are logs separated from primary output?
- Are Linux and macOS platform differences handled clearly?
- Are the CLI flows covered by `pytest`?

## Implementation Bias

When choosing between a prettier interface and a more reliable one, prefer reliability.

When choosing between cleverness and predictability, prefer predictability.

When choosing between a dense dashboard and a simple readable summary, prefer the readable summary.

## Guardrails

- do not replace machine-relevant output with decorative formatting
- do not use `Live` or animation where snapshot-like output is more stable
- prefer stable labels and semantics so CLI tests remain deterministic
- use Rich to clarify operator workflows, not to make the terminal busy
