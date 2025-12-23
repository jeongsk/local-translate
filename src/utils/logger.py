"""Logging configuration with structured logging and rotation."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "local_translate",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> logging.Logger:
    """
    Configure and return a logger with console and file handlers.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file. If None, uses default location
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create formatters
    console_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)8s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)8s] %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if log_file specified)
    if log_file is None:
        # Default log location
        log_dir = Path.home() / ".local_translate" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "translation.log"
    else:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    logger.info(f"Logger initialized: {name}")
    logger.info(f"Log file: {log_file}")

    return logger


def get_logger(name: str = "local_translate") -> logging.Logger:
    """
    Get or create a logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # Initialize if not already configured
    if not logger.handlers:
        setup_logger(name)

    return logger


# Module-level logger for utility functions
_logger = get_logger(__name__)
