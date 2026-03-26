from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path

from {{PYTHON_PACKAGE_NAME}}.application.task_service import TaskService
from {{PYTHON_PACKAGE_NAME}}.config import load_settings
from {{PYTHON_PACKAGE_NAME}}.infrastructure.file_task_store import FileTaskStore
from {{PYTHON_PACKAGE_NAME}}.infrastructure.logging import configure_logging


def run_worker(
    *,
    once: bool,
    seed_demo_if_empty: bool,
    log_file: Path | None,
    log_level: str | None,
    max_iterations: int | None,
) -> int:
    settings = load_settings()
    settings.ensure_runtime_dirs()
    configure_logging(log_level or settings.log_level, log_file=log_file)

    store = FileTaskStore(settings.state_dir)
    service = TaskService(store)

    if seed_demo_if_empty and not any(task.status == "pending" for task in service.list_tasks()):
        service.seed_demo_task()

    iterations = 0
    while True:
        iterations += 1
        task = service.process_next_task()
        if task is None:
            logging.info("No pending tasks available.")
        else:
            logging.info("Processed task %s", task.id)

        if once:
            return 0
        if max_iterations is not None and iterations >= max_iterations:
            return 0
        time.sleep(settings.worker_poll_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the project worker loop.")
    parser.add_argument("--once", action="store_true", help="Process at most one iteration and exit.")
    parser.add_argument(
        "--seed-demo-if-empty",
        action="store_true",
        help="Create a demo task before running when no pending tasks exist.",
    )
    parser.add_argument("--log-file", type=Path, help="Optional file path for operator-visible logs.")
    parser.add_argument("--log-level", help="Override the configured log level.")
    parser.add_argument("--max-iterations", type=int, help="Stop after this many loop iterations.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return run_worker(
        once=args.once,
        seed_demo_if_empty=args.seed_demo_if_empty,
        log_file=args.log_file,
        log_level=args.log_level,
        max_iterations=args.max_iterations,
    )


if __name__ == "__main__":
    raise SystemExit(main())
