"""Centralized logging configuration for Curriculum Repository System."""

import logging
import logging.config
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from curriculum.config import settings


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    enable_file_logging: bool = True,
    enable_json_logging: bool = False,
) -> logging.Logger:
    """
    Configure centralized logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (defaults to ./logs/curriculum.log)
        enable_file_logging: Whether to log to file
        enable_json_logging: Whether to use JSON formatting (for structured logging)

    Returns:
        Configured logger instance
    """
    # Determine log level
    level = getattr(logging, (log_level or settings.log_level).upper(), logging.INFO)

    # Determine log file path
    if log_file is None:
        log_dir = Path("./logs")
        log_dir.mkdir(exist_ok=True)
        log_file = str(log_dir / "curriculum.log")

    # Determine formatters based on JSON preference
    if enable_json_logging:
        formatter = create_json_formatter()
    else:
        formatter = create_standard_formatter()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Add file handler if enabled
    if enable_file_logging:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Prevent propagation to avoid duplicate logs
    root_logger.propagate = False

    # Create application logger
    app_logger = logging.getLogger("curriculum")
    app_logger.setLevel(level)

    return app_logger


def create_standard_formatter() -> logging.Formatter:
    """Create standard text formatter for logs."""
    format_string = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "%(funcName)s:%(lineno)d - %(message)s"
    )
    return logging.Formatter(
        fmt=format_string,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def create_json_formatter() -> logging.Formatter:
    """Create JSON formatter for structured logging."""
    try:
        import json_log_formatter

        formatter = json_log_formatter.JSONFormatter()
        return formatter
    except ImportError:
        # Fallback to standard formatter if json-log-formatter not installed
        logging.warning("json-log-formatter not installed, using standard formatter")
        return create_standard_formatter()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def configure_third_party_logging() -> None:
    """Configure logging levels for third-party libraries."""
    # Reduce noise from verbose libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)


# Initialize logging on module import
logger = setup_logging()
configure_third_party_logging()

