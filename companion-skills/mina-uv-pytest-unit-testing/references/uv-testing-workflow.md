# UV Testing Workflow

Use this reference when the immediate test problem may actually be a `uv` package, environment, workspace, or tool-management problem.

## Package Baseline

- Prefer the `uv init --package` mental model for package-style repos.
- Expect the project to behave like an installable package with code under `src/<package>/`.
- When imports fail, check whether the package/install model is wrong before patching around it in tests.

## Environment Sync

- If dependencies, editable installs, or lock state may be stale, run `uv sync` first.
- If the dependency graph changed and the lockfile is out of date, refresh with `uv lock` and then `uv sync`.
- Treat environment drift as a first-class reason for test failures before changing pytest config or test code.

## Workspace Cautions

- Only apply this section when the Mina repo actually becomes a `uv` workspace.
- Workspace roots still need their own distinct `[project] name`.
- Local inter-package dependencies should use `[tool.uv.sources]` with `workspace = true`.
- If workspace packages are not wired correctly, pytest failures may show up as import or resolution problems even when the tests are fine.

## Tool Management

- Keep project test dependencies inside the project environment.
- Use `uv tool install` only for standalone developer tools that are intentionally managed outside the project.
- Use `uv tool upgrade` when an externally managed tool drifts, but do not confuse that with project dependency management.
- Do not substitute global tools for project-owned pytest, coverage, or lint/typecheck dependencies unless the repo explicitly documents that model.
