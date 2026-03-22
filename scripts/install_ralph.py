#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from template_utils import copy_rendered_tree, load_answers


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the Ralph loop template into a target repo.")
    parser.add_argument("--repo-root", required=True, help="Target repository root.")
    parser.add_argument(
        "--answers",
        help="Optional answers JSON used for placeholder substitution inside copied Ralph assets.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files instead of skipping them.",
    )
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parent.parent
    repo_root = Path(args.repo_root).expanduser().resolve()
    answers = (
        load_answers(Path(args.answers).expanduser().resolve())
        if args.answers
        else {}
    )

    source_root = skill_root / "assets" / "templates" / "ralph"
    copy_rendered_tree(
        source_root,
        repo_root,
        answers,
        allow_missing=True,
        overwrite=args.overwrite,
    )

    print(f"Installed Ralph assets into {repo_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
