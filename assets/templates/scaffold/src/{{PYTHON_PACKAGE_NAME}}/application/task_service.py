from __future__ import annotations

from typing import Protocol

from {{PYTHON_PACKAGE_NAME}}.domain.task import Task


class TaskStore(Protocol):
    def read_tasks(self) -> list[Task]: ...

    def write_tasks(self, tasks: list[Task]) -> None: ...

    def read_processed(self) -> list[Task]: ...

    def write_processed(self, tasks: list[Task]) -> None: ...


class TaskService:
    def __init__(self, store: TaskStore) -> None:
        self.store = store

    def list_tasks(self) -> list[Task]:
        return self.store.read_tasks()

    def list_processed_tasks(self) -> list[Task]:
        return self.store.read_processed()

    def seed_demo_task(self) -> Task:
        tasks = self.store.read_tasks()
        for task in tasks:
            if task.id == "demo-bootstrap-task" and task.status == "pending":
                return task

        task = Task(id="demo-bootstrap-task", description="Demo bootstrap task")
        tasks.append(task)
        self.store.write_tasks(tasks)
        return task

    def process_next_task(self) -> Task | None:
        tasks = self.store.read_tasks()
        for index, task in enumerate(tasks):
            if task.status != "pending":
                continue

            processed = task.mark_processed()
            tasks[index] = processed
            self.store.write_tasks(tasks)

            processed_tasks = self.store.read_processed()
            processed_tasks.append(processed)
            self.store.write_processed(processed_tasks)
            return processed

        return None
