"""
Logging Module

Centralized logging configuration for the application.

Design Decisions:
- Structured logging with JSON format for production
- Different log levels per environment
- Request ID tracking for tracing
- Separate loggers for different modules
"""

import logging
import sys
from typing import Optional
from datetime import datetime
from app.config import settings

# ANSI color codes for console output
class LogColors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter with colors for console output.
    Makes logs easier to read during development.
    """
    
    COLORS = {
        logging.DEBUG: LogColors.GRAY,
        logging.INFO: LogColors.CYAN,
        logging.WARNING: LogColors.YELLOW,
        logging.ERROR: LogColors.RED,
        logging.CRITICAL: LogColors.MAGENTA,
    }
    
    def format(self, record):
        # Add color based on log level
        color = self.COLORS.get(record.levelno, LogColors.RESET)
        record.levelname = f"{color}{record.levelname}{LogColors.RESET}"
        record.name = f"{LogColors.BLUE}{record.name}{LogColors.RESET}"
        return super().format(record)


def setup_logging():
    """
    Configure application-wide logging.
    
    - Development: Colored console output with DEBUG level
    - Production: JSON format with INFO level
    """
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level))
    
    # Format
    if settings.is_development:
        # Colored format for development
        formatter = ColoredFormatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        # Simple format for production (use JSON logger in real prod)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Silence noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    
    Usage:
        logger = get_logger(__name__)
        logger.info("Something happened")
    """
    return logging.getLogger(name)


# Initialize logging on module import
setup_logging()

# Module logger
logger = get_logger(__name__)


# Request logging helper
def log_request(method: str, path: str, status_code: int, duration_ms: float, user_id: Optional[int] = None):
    """
    Log HTTP request with structured data.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        user_id: Optional user ID
    """
    user_info = f"user_id={user_id}" if user_id else "anonymous"
    logger.info(
        f"{method} {path} - {status_code} - {duration_ms:.2f}ms - {user_info}"
    )


# Error logging helper
def log_error(error: Exception, context: Optional[dict] = None):
    """
    Log error with context.
    
    Args:
        error: Exception instance
        context: Optional context dict (user_id, company_id, etc.)
    """
    context_str = f" | Context: {context}" if context else ""
    logger.error(f"{type(error).__name__}: {str(error)}{context_str}", exc_info=True)


if __name__ == "__main__":
    # Test logging
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
