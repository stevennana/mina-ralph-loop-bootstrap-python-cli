from __future__ import annotations

import json
from pathlib import Path

from {{PYTHON_PACKAGE_NAME}}.domain.task import Task


class FileTaskStore:
    def __init__(self, state_dir: Path) -> None:
        self.state_dir = state_dir
        self.queue_file = state_dir / "queue.json"
        self.processed_file = state_dir / "processed.json"

    def _ensure_runtime(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _read_file(self, path: Path) -> list[Task]:
        self._ensure_runtime()
        if not path.exists():
            return []

        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError(f"Expected a list in {path}")
        return [Task.from_dict(item) for item in payload]

    def _write_file(self, path: Path, tasks: list[Task]) -> None:
        self._ensure_runtime()
        serialized = [task.to_dict() for task in tasks]
        path.write_text(json.dumps(serialized, indent=2), encoding="utf-8")

    def read_tasks(self) -> list[Task]:
        return self._read_file(self.queue_file)

    def write_tasks(self, tasks: list[Task]) -> None:
        self._write_file(self.queue_file, tasks)

    def read_processed(self) -> list[Task]:
        return self._read_file(self.processed_file)

    def write_processed(self, tasks: list[Task]) -> None:
        self._write_file(self.processed_file, tasks)
