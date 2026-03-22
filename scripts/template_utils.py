from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
from typing import Any, Iterable


PLACEHOLDER_PATTERN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def load_answers_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Answers JSON must be an object.")
    return data


def load_answers(path: Path) -> dict[str, str]:
    data = load_answers_json(path)
    normalized: dict[str, str] = {}
    for key, value in data.items():
        if not isinstance(key, str):
            raise ValueError("All answer keys must be strings.")
        normalized[key] = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
    return normalized


def render_text(text: str, answers: dict[str, str], allow_missing: bool) -> tuple[str, list[str]]:
    missing: list[str] = []

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key in answers:
            return answers[key]
        missing.append(key)
        return match.group(0) if allow_missing else ""

    rendered = PLACEHOLDER_PATTERN.sub(replace, text)
    return rendered, missing


def copy_rendered_tree(
    source_root: Path,
    destination_root: Path,
    answers: dict[str, str],
    *,
    allow_missing: bool = False,
    overwrite: bool = False,
) -> list[str]:
    missing_keys: list[str] = []
    for source in sorted(source_root.rglob("*")):
        relative = source.relative_to(source_root)
        destination = destination_root / relative

        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and not overwrite:
            continue

        if source.suffix in {".png", ".jpg", ".jpeg", ".svg", ".woff", ".woff2", ".ttf"}:
            shutil.copy2(source, destination)
            continue

        rendered, missing = render_text(source.read_text(encoding="utf-8"), answers, allow_missing)
        missing_keys.extend(missing)
        destination.write_text(rendered, encoding="utf-8")

    return sorted(set(missing_keys))


def parse_args_list(values: Iterable[str]) -> list[Path]:
    return [Path(value).expanduser().resolve() for value in values]
