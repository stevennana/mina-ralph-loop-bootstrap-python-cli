#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


TASKMETA_PATTERN = re.compile(r"```json taskmeta\s*([\s\S]*?)```", re.MULTILINE)


@dataclass
class TaskDoc:
    file_path: Path
    markdown: str
    meta: dict[str, object]

    @property
    def id(self) -> str:
        return str(self.meta.get("id", self.file_path.stem)).strip()

    @property
    def order(self) -> int:
        value = self.meta.get("order")
        try:
            return int(value) if value is not None else 10**9
        except (TypeError, ValueError):
            return 10**9


def timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def extract_task_meta(markdown: str) -> dict[str, object]:
    match = TASKMETA_PATTERN.search(markdown)
    if not match:
        raise ValueError("Task markdown does not contain a json taskmeta block.")
    return json.loads(match.group(1).strip())


def replace_task_meta(markdown: str, meta: dict[str, object]) -> str:
    rendered = json.dumps(meta, ensure_ascii=False, indent=2)
    replacement = f"```json taskmeta\n{rendered}\n```"
    return TASKMETA_PATTERN.sub(replacement, markdown, count=1)


def append_progress_note(markdown: str, note: str) -> str:
    marker = "## Progress log"
    if marker not in markdown:
        return markdown.rstrip() + f"\n\n{marker}\n\n- {note}\n"

    pattern = re.compile(r"## Progress log\s*([\s\S]*)$", re.MULTILINE)

    def _replace(match: re.Match[str]) -> str:
        tail = match.group(1).strip()
        if tail:
            return f"{marker}\n\n{tail}\n- {note}\n"
        return f"{marker}\n\n- {note}\n"

    return pattern.sub(_replace, markdown, count=1)


def extract_objective(markdown: str) -> str:
    match = re.search(r"^## Objective\s+([\s\S]*?)(?=^## |\Z)", markdown, re.MULTILINE)
    if not match:
        return ""
    return " ".join(line.strip() for line in match.group(1).strip().splitlines() if line.strip())


def list_task_docs(dir_path: Path) -> list[TaskDoc]:
    if not dir_path.exists():
        return []
    docs: list[TaskDoc] = []
    for path in sorted(dir_path.glob("*.md")):
        markdown = path.read_text(encoding="utf-8")
        match = TASKMETA_PATTERN.search(markdown)
        if not match:
            continue
        docs.append(TaskDoc(path, markdown, json.loads(match.group(1).strip())))
    docs.sort(key=lambda doc: (doc.order, doc.file_path.name))
    return docs


def write_active_index(repo_root: Path, active_tasks: list[TaskDoc]) -> None:
    lines = [
        "# Ralph Loop Task Queue",
        "",
        f"This queue is the task-level promotion source of truth for {repo_root.name}.",
        "",
        "Only task files in this directory that contain a `taskmeta` JSON block are eligible for automatic selection, evaluation, and promotion.",
        "",
        "## Current recommended sequence",
    ]
    if active_tasks:
        for index, task in enumerate(active_tasks, start=1):
            objective = extract_objective(task.markdown) or str(task.meta.get("title") or task.id)
            lines.append(f"{index}. `{task.file_path.name}` -> {objective}")
    else:
        lines.append("The current active queue is exhausted. Review completed plans, update the docs, and seed the next active wave.")

    lines.extend(
        [
            "",
            "## Operating rule",
            "",
            "A task may be promoted only when all of the following are true:",
            "",
            "- deterministic checks pass",
            "- the evaluator marks the task as `done`",
            "- the evaluator recommends promotion",
            "- the task metadata declares a `next_task_on_success`, or explicitly declares that the queue ends here",
            "",
            "## When this queue ends",
            "",
            "When the active sequence is exhausted, do not continue with ad hoc prompts alone.",
            "Update the relevant product specs and design docs first, then seed the next active queue for the next feature wave.",
            "",
        ]
    )
    (repo_root / "docs" / "exec-plans" / "active" / "index.md").write_text("\n".join(lines), encoding="utf-8")


def write_state(repo_root: Path, current_task_id: str | None, completed_tasks: list[TaskDoc], active_tasks: list[TaskDoc], history_note: str | None) -> None:
    state_dir = repo_root / "state"
    ensure_dir(state_dir)

    defaults = {
        "README.md": (
            "# State Directory\n\n"
            "These files are mutable runtime artifacts for the Ralph loop.\n\n"
            "- `current-task.txt`: the active task id\n"
            "- `last-result.txt`: final message from the last worker Codex run\n"
            "- `evaluation.json`: latest deterministic + evaluator result\n"
            "- `task-history.md`: promotion history\n"
            "- `run-log.md`: append-only operational log\n"
            "- `backlog.md`: rendered queue snapshot\n"
        ),
        "last-result.txt": "",
        "evaluation.json": '{\n  "status": "not_run"\n}\n',
        "current-cycle.json": '{\n  "status": "idle"\n}\n',
        "run-log.md": "# Ralph Loop Run Log\n",
        "task-history.md": "# Task History\n\n",
    }
    for filename, content in defaults.items():
        path = state_dir / filename
        if not path.exists():
            path.write_text(content, encoding="utf-8")

    (state_dir / "current-task.txt").write_text(f"{current_task_id or 'NONE'}\n", encoding="utf-8")

    backlog_lines = ["# Backlog", ""]
    for task in sorted(completed_tasks + active_tasks, key=lambda doc: (doc.order, doc.file_path.name)):
        marker = "x" if str(task.meta.get("status")) == "completed" else " "
        current_tag = " ← current" if current_task_id and task.id == current_task_id else ""
        backlog_lines.append(f"- [{marker}] {task.id} — {task.meta.get('title')}{current_tag}")
    backlog_lines.append("")
    (state_dir / "backlog.md").write_text("\n".join(backlog_lines), encoding="utf-8")

    if history_note:
        history_path = state_dir / "task-history.md"
        with history_path.open("a", encoding="utf-8") as handle:
            handle.write(f"- {history_note}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Mark bootstrap foundation complete and leave feature tasks for Ralph.")
    parser.add_argument("--repo-root", required=True, help="Target repository root.")
    parser.add_argument("--bootstrap-task-id", default="010-bootstrap-foundation", help="Bootstrap task id to archive.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).expanduser().resolve()
    active_dir = repo_root / "docs" / "exec-plans" / "active"
    completed_dir = repo_root / "docs" / "exec-plans" / "completed"
    ensure_dir(completed_dir)

    active_tasks = list_task_docs(active_dir)
    completed_tasks = list_task_docs(completed_dir)

    bootstrap_task = next((task for task in active_tasks if task.id == args.bootstrap_task_id), None)
    history_note: str | None = None

    if bootstrap_task:
        completed_at = timestamp()
        next_task_id = str(bootstrap_task.meta.get("next_task_on_success") or "").strip() or None
        updated_meta = dict(bootstrap_task.meta)
        updated_meta["status"] = "completed"
        updated_meta["completed_at"] = completed_at
        completed_markdown = replace_task_meta(bootstrap_task.markdown, updated_meta)
        completed_markdown = append_progress_note(
            completed_markdown,
            f"{completed_at}: automatically completed by the bootstrap skill after docs, scaffold, Ralph wiring, and verify succeeded.",
        )
        completed_path = completed_dir / bootstrap_task.file_path.name
        completed_path.write_text(completed_markdown, encoding="utf-8")
        bootstrap_task.file_path.unlink()
        history_note = f"{completed_at}: bootstrap finalized {bootstrap_task.id} -> {next_task_id or 'NONE'}"

    active_tasks = list_task_docs(active_dir)
    completed_tasks = list_task_docs(completed_dir)

    # Repair older generated repos that left feature tasks in active/
    # while already marking them completed. Only the foundation task
    # should be auto-completed by the bootstrap session.
    repaired_any = False
    for index, task in enumerate(active_tasks):
        current_status = str(task.meta.get("status") or "")
        if current_status != "completed":
            continue
        updated_meta = dict(task.meta)
        updated_meta.pop("completed_at", None)
        updated_meta["status"] = "active" if index == 0 else "queued"
        repaired_markdown = replace_task_meta(task.markdown, updated_meta)
        repaired_markdown = append_progress_note(
            repaired_markdown,
            f"{timestamp()}: reset from completed to {updated_meta['status']} because feature tasks must remain for the Ralph loop after bootstrap handoff.",
        )
        task.file_path.write_text(repaired_markdown, encoding="utf-8")
        repaired_any = True

    if repaired_any:
        active_tasks = list_task_docs(active_dir)
        completed_tasks = list_task_docs(completed_dir)

    next_task = next((task for task in active_tasks if str(task.meta.get("status")) in {"active", "queued"}), None)
    if next_task:
        for idx, task in enumerate(active_tasks):
            desired_status = "active" if idx == 0 else "queued"
            if str(task.meta.get("status")) == desired_status:
                continue
            updated_meta = dict(task.meta)
            updated_meta["status"] = desired_status
            task.file_path.write_text(replace_task_meta(task.markdown, updated_meta), encoding="utf-8")
        active_tasks = list_task_docs(active_dir)
        next_task = active_tasks[0]

    current_task_id = next_task.id if next_task else None
    write_active_index(repo_root, active_tasks)
    write_state(repo_root, current_task_id, completed_tasks, active_tasks, history_note)

    print(f"Finalized bootstrap state in {repo_root}")
    if current_task_id:
        print(f"Next Ralph task: {current_task_id}")
    else:
        print("No remaining active tasks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
