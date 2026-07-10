"""
Structured logging setup for VoidRemote.

Configures rotating file logs and colored console output with
consistent formatting across the entire application.
"""

from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

# ANSI color codes for terminal output
COLORS = {
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "DIM": "\033[2m",
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "MAGENTA": "\033[95m",
    "CYAN": "\033[96m",
    "WHITE": "\033[97m",
    "GREY": "\033[90m",
}

LEVEL_COLORS: dict[int, str] = {
    logging.DEBUG: COLORS["CYAN"],
    logging.INFO: COLORS["GREEN"],
    logging.WARNING: COLORS["YELLOW"],
    logging.ERROR: COLORS["RED"],
    logging.CRITICAL: COLORS["MAGENTA"] + COLORS["BOLD"],
}


class ColoredFormatter(logging.Formatter):
    """Log formatter that adds ANSI color to console output."""

    def __init__(self, fmt: Optional[str] = None, use_color: bool = True) -> None:
        super().__init__(fmt)
        self.use_color = use_color and sys.stdout.isatty()

    def format(self, record: logging.LogRecord) -> str:
        original_levelname = record.levelname
        if self.use_color:
            color = LEVEL_COLORS.get(record.levelno, COLORS["RESET"])
            record.levelname = f"{color}{record.levelname:<8}{COLORS['RESET']}"
            record.name = f"{COLORS['BLUE']}{record.name}{COLORS['RESET']}"
        result = super().format(record)
        record.levelname = original_levelname
        return result


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    console: bool = True,
    console_color: bool = True,
    fmt: Optional[str] = None,
) -> None:
    """
    Configure application-wide logging.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Optional path to write rotating log file.
        max_bytes: Max size of each log file before rotation.
        backup_count: Number of backup log files to keep.
        console: Whether to output logs to stderr.
        console_color: Whether to colorize console output.
        fmt: Custom log format string.
    """
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates on re-init
    root.handlers.clear()

    log_format = fmt or "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    if console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(
            ColoredFormatter(fmt=log_format, use_color=console_color)
        )
        root.addHandler(console_handler)

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(
            logging.Formatter(fmt=log_format, datefmt=date_format)
        )
        root.addHandler(file_handler)

    # Silence noisy third-party loggers
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("adb_shell").setLevel(logging.WARNING)

    logging.getLogger(__name__).debug(
        "Logging configured: level=%s, file=%s", level, log_file
    )


def get_logger(name: str) -> logging.Logger:
    """Return a logger for the given module name."""
    return logging.getLogger(name)
