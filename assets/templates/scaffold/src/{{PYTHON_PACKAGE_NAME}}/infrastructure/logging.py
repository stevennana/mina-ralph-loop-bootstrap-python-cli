from __future__ import annotations

import logging
from pathlib import Path

from rich.logging import RichHandler


def configure_logging(log_level: str, *, log_file: Path | None = None) -> None:
    level = getattr(logging, log_level.upper(), logging.INFO)
    handlers: list[logging.Handler] = [RichHandler(rich_tracebacks=True, show_path=False)]
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        handlers.append(file_handler)

    logging.basicConfig(level=level, format="%(message)s", handlers=handlers, force=True)
