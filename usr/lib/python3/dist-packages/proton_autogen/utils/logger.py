# proton_autogen/utils/logger.py
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class JsonFormatter(logging.Formatter):
    """Format log records as JSON."""

    RESERVED = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "process",
        "processName",
        "message",
    }

    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": datetime.fromtimestamp(
                record.created,
                tz=timezone.utc,
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        # Extra fields
        for key, value in record.__dict__.items():
            if key not in self.RESERVED and not key.startswith("_") and value is not None:
                log[key] = value

        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)

        return json.dumps(log, default=str, ensure_ascii=False)


class StructuredLogger:
    """Structured logger with JSON file output."""

    def __init__(
        self,
        name: str,
        level: int = logging.INFO,
    ) -> None:

        self.logger = logging.getLogger(name)

        if self.logger.handlers:
            return

        self.logger.setLevel(level)
        self.logger.propagate = False

        log_dir = Path.home() / ".local/share/proton-autogen/logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        #
        # JSON file
        #
        file_handler = logging.FileHandler(
            log_dir / "proton-autogen.json",
            encoding="utf-8",
        )
        file_handler.setFormatter(JsonFormatter())

        #
        # Console
        #
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter(
                "[%(levelname)s] %(name)s: %(message)s"
            )
        )

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def debug(
        self,
        message: str,
        *args: Any,
        **fields: Any,
    ) -> None:
        self.logger.debug(message, *args, extra=fields)

    def info(
        self,
        message: str,
        *args: Any,
        **fields: Any,
    ) -> None:
        self.logger.info(message, *args, extra=fields)

    def warning(self, message: str, **fields: Any) -> None:
        self.logger.warning(message, extra=fields)

    def warn(self, message: str, **fields: Any) -> None:
        self.logger.warning(message, extra=fields)

    def error(
        self,
        message: str,
        *,
        exc_info: bool | Exception = False,
        **fields: Any,
    ) -> None:
        self.logger.error(
            message,
            extra=fields,
            exc_info=exc_info,
        )

    def exception(self, message: str, **fields: Any) -> None:
        self.logger.exception(message, extra=fields)

    def critical(self, message: str, **fields: Any) -> None:
        self.logger.critical(message, extra=fields)
