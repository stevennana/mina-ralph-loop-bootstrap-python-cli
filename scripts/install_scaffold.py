#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from template_utils import copy_rendered_tree, load_answers


def _slugify(raw: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", raw.strip().lower())
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned or "app"


def _package_name(raw: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", raw.strip().lower().replace("-", "_"))
    cleaned = re.sub(r"_{2,}", "_", cleaned).strip("_")
    if not cleaned:
        cleaned = "app"
    if cleaned[0].isdigit():
        cleaned = f"app_{cleaned}"
    return cleaned


def _env_prefix(raw: str) -> str:
    cleaned = re.sub(r"[^A-Z0-9]+", "_", raw.strip().upper())
    cleaned = re.sub(r"_{2,}", "_", cleaned).strip("_")
    return cleaned or "APP"


def derive_scaffold_answers(base_answers: dict[str, str], repo_root: Path) -> dict[str, str]:
    answers = dict(base_answers)
    project_name = answers.get("PROJECT_NAME") or repo_root.name
    one_line_product = answers.get("ONE_LINE_PRODUCT") or f"Python CLI for {project_name}"
    dist_name = answers.get("DIST_PACKAGE_NAME") or _slugify(project_name)
    cli_command = answers.get("CLI_COMMAND_NAME") or dist_name
    package_name = answers.get("PYTHON_PACKAGE_NAME") or _package_name(cli_command)
    env_prefix = answers.get("ENV_PREFIX") or _env_prefix(cli_command)

    answers.update(
        {
            "PROJECT_NAME": project_name,
            "ONE_LINE_PRODUCT": one_line_product,
            "DIST_PACKAGE_NAME": dist_name,
            "CLI_COMMAND_NAME": cli_command,
            "PYTHON_PACKAGE_NAME": package_name,
            "ENV_PREFIX": env_prefix,
        }
    )
    return answers


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the Python CLI scaffold template into a target repo.")
    parser.add_argument("--repo-root", required=True, help="Target repository root.")
    parser.add_argument(
        "--answers",
        help="Optional answers JSON used for placeholder substitution inside scaffold assets.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files instead of skipping them.",
    )
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parent.parent
    repo_root = Path(args.repo_root).expanduser().resolve()
    answers = load_answers(Path(args.answers).expanduser().resolve()) if args.answers else {}
    answers = derive_scaffold_answers(answers, repo_root)

    source_root = skill_root / "assets" / "templates" / "scaffold"
    missing = copy_rendered_tree(
        source_root,
        repo_root,
        answers,
        allow_missing=False,
        overwrite=args.overwrite,
    )
    if missing:
        print("Missing placeholders:", ", ".join(missing), file=sys.stderr)
        return 1

    print(f"Installed scaffold assets into {repo_root}")
    print(f"CLI command: {answers['CLI_COMMAND_NAME']}")
    print(f"Python package: {answers['PYTHON_PACKAGE_NAME']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
