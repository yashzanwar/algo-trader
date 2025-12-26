"""Logging configuration for the AlgoTrader framework."""

from __future__ import annotations

import logging
import sys
from typing import Literal

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def setup_logging(
    level: LogLevel = "INFO",
    log_file: str | None = None,
    format_string: str | None = None,
) -> logging.Logger:
    """Configure structured logging for the framework.
    
    Args:
        level: Logging level
        log_file: Optional file path for log output
        format_string: Custom format string
        
    Returns:
        Configured logger instance
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logger = logging.getLogger("algotrader")
    logger.setLevel(getattr(logging, level))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))
    console_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level))
        file_handler.setFormatter(logging.Formatter(format_string))
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"algotrader.{name}")
