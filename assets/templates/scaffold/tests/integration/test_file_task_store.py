from __future__ import annotations

import pytest

from {{PYTHON_PACKAGE_NAME}}.domain.task import Task
from {{PYTHON_PACKAGE_NAME}}.infrastructure.file_task_store import FileTaskStore


@pytest.mark.integration
def test_file_task_store_round_trips_queue_and_processed_tasks(tmp_path) -> None:
    store = FileTaskStore(tmp_path)
    pending = Task(id="task-1", description="Round-trip queue test")
    processed = pending.mark_processed()

    store.write_tasks([pending, processed])
    store.write_processed([processed])

    queue = store.read_tasks()
    archive = store.read_processed()

    assert [task.id for task in queue] == ["task-1", "task-1"]
    assert queue[1].status == "processed"
    assert [task.id for task in archive] == ["task-1"]
