from __future__ import annotations

from {{PYTHON_PACKAGE_NAME}}.application.task_service import TaskService
from {{PYTHON_PACKAGE_NAME}}.domain.task import Task


class InMemoryTaskStore:
    def __init__(self) -> None:
        self.tasks: list[Task] = []
        self.processed: list[Task] = []

    def read_tasks(self) -> list[Task]:
        return list(self.tasks)

    def write_tasks(self, tasks: list[Task]) -> None:
        self.tasks = list(tasks)

    def read_processed(self) -> list[Task]:
        return list(self.processed)

    def write_processed(self, tasks: list[Task]) -> None:
        self.processed = list(tasks)


def test_seed_and_process_demo_task() -> None:
    store = InMemoryTaskStore()
    service = TaskService(store)

    seeded = service.seed_demo_task()
    processed = service.process_next_task()

    assert seeded.id == "demo-bootstrap-task"
    assert processed is not None
    assert processed.status == "processed"
    assert len(service.list_processed_tasks()) == 1
