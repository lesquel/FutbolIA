"""
FutbolIA - Structured Logger
Centralized logging with JSON format for production
"""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from src.core.config import settings


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for production environments"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, "extra_data"):
            log_data["data"] = record.extra_data

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Colored output for development"""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[41m",  # Red background
    }
    RESET = "\033[0m"
    ICONS = {
        "DEBUG": "🔍",
        "INFO": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "CRITICAL": "🔥",
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        icon = self.ICONS.get(record.levelname, "")

        # Format timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Build message
        message = (
            f"{color}{icon} [{timestamp}] {record.levelname}: {record.getMessage()}{self.RESET}"
        )

        # Add extra data if present
        if hasattr(record, "extra_data") and record.extra_data:
            message += f"\n   📊 Data: {record.extra_data}"

        return message


def get_logger(name: str = "futbolia") -> logging.Logger:
    """
    Get a configured logger instance

    Usage:
        from src.core.logger import get_logger
        logger = get_logger(__name__)

        logger.info("Prediction started", extra={"extra_data": {"team": "Real Madrid"}})
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

        # Create handler
        handler = logging.StreamHandler(sys.stdout)

        # Use JSON format in production, colored in development
        if settings.ENVIRONMENT == "production":
            handler.setFormatter(JSONFormatter())
        else:
            handler.setFormatter(ColoredFormatter())

        logger.addHandler(handler)
        logger.propagate = False

    return logger


# Convenience functions for quick logging
_default_logger = None


def _get_default_logger() -> logging.Logger:
    global _default_logger
    if _default_logger is None:
        _default_logger = get_logger("futbolia")
    return _default_logger


def log_info(message: str, **kwargs: Any) -> None:
    """Quick info log"""
    logger = _get_default_logger()
    if kwargs:
        logger.info(message, extra={"extra_data": kwargs})
    else:
        logger.info(message)


def log_warning(message: str, **kwargs: Any) -> None:
    """Quick warning log"""
    logger = _get_default_logger()
    if kwargs:
        logger.warning(message, extra={"extra_data": kwargs})
    else:
        logger.warning(message)


def log_error(message: str, **kwargs: Any) -> None:
    """Quick error log"""
    logger = _get_default_logger()
    if kwargs:
        logger.error(message, extra={"extra_data": kwargs})
    else:
        logger.error(message)


def log_debug(message: str, **kwargs: Any) -> None:
    """Quick debug log"""
    logger = _get_default_logger()
    if kwargs:
        logger.debug(message, extra={"extra_data": kwargs})
    else:
        logger.debug(message)


def log_prediction(
    home_team: str, away_team: str, winner: str, confidence: float, user_id: str | None = None
) -> None:
    """Log a prediction event"""
    log_info(
        f"Prediction: {home_team} vs {away_team}",
        home_team=home_team,
        away_team=away_team,
        winner=winner,
        confidence=confidence,
        user_id=user_id,
    )


def log_api_call(
    endpoint: str, method: str, status_code: int, duration_ms: float, user_id: str | None = None
) -> None:
    """Log an API call"""
    log_info(
        f"API {method} {endpoint} -> {status_code}",
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        duration_ms=duration_ms,
        user_id=user_id,
    )
