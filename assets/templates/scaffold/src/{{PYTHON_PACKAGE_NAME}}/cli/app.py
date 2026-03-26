from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from {{PYTHON_PACKAGE_NAME}}.application.task_service import TaskService
from {{PYTHON_PACKAGE_NAME}}.config import Settings, load_settings
from {{PYTHON_PACKAGE_NAME}}.infrastructure.file_task_store import FileTaskStore


app = typer.Typer(
    help="{{ONE_LINE_PRODUCT}}",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)
task_app = typer.Typer(help="Inspect and seed the local task queue.")
app.add_typer(task_app, name="task")
console = Console()


def _build_service() -> tuple[Settings, TaskService]:
    settings = load_settings()
    settings.ensure_runtime_dirs()
    store = FileTaskStore(settings.state_dir)
    return settings, TaskService(store)


@app.command()
def doctor() -> None:
    """Print the current harness and runtime status."""
    settings, service = _build_service()
    table = Table(title="Harness status")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("CLI command", "{{CLI_COMMAND_NAME}}")
    table.add_row("Python package", "{{PYTHON_PACKAGE_NAME}}")
    table.add_row("State dir", str(settings.state_dir))
    table.add_row("Logs dir", str(settings.logs_dir))
    table.add_row("Pending tasks", str(sum(task.status == "pending" for task in service.list_tasks())))
    table.add_row("Processed tasks", str(len(service.list_processed_tasks())))
    console.print(table)


@task_app.command("seed-demo")
def seed_demo() -> None:
    """Create a small demo task so the worker path has something to process."""
    _, service = _build_service()
    task = service.seed_demo_task()
    console.print(f"Ready task: [bold]{task.id}[/bold]")


@task_app.command("list")
def list_tasks() -> None:
    """List all queued tasks."""
    _, service = _build_service()
    tasks = service.list_tasks()
    if not tasks:
        console.print("No tasks queued.")
        return

    table = Table(title="Queued tasks")
    table.add_column("Task ID")
    table.add_column("Description")
    table.add_column("Status")
    for task in tasks:
        table.add_row(task.id, task.description, task.status)
    console.print(table)


def main() -> None:
    app()
