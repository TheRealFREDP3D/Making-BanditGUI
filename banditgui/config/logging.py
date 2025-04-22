"""
Logging configuration for BanditGUI.

This module sets up logging for the application.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logging(log_level: str = 'INFO', log_file: Optional[str] = None) -> None:
    """
    Set up logging for the application.

    Args:
        log_level: The log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to the log file, if None, logs to console only
    """
    # Convert log level string to logging level
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    # Create logger
    logger = logging.getLogger('banditgui')
    logger.setLevel(numeric_level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Create file handler if log file is specified
    if log_file:
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Create rotating file handler (10 MB max size, keep 5 backups)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent logs from being propagated to the root logger
    logger.propagate = False

    logger.info(f"Logging initialized with level {log_level}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.

    Args:
        name: The name of the logger

    Returns:
        logging.Logger: The logger
    """
    return logging.getLogger(f'banditgui.{name}')
