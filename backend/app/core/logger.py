import logging
import os
from typing import Any

# Configure logging based on environment
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Create logger
logger = logging.getLogger("specsharp")
logger.setLevel(getattr(logging, LOG_LEVEL.upper()))

# Create handler
handler = logging.StreamHandler()
handler.setLevel(getattr(logging, LOG_LEVEL.upper()))

# Create formatter
if ENVIRONMENT == "production":
    formatter = logging.Formatter(
        '{"time": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}'
    )
else:
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

handler.setFormatter(formatter)
logger.addHandler(handler)

def log_debug(message: str, **kwargs: Any) -> None:
    """Log debug message with context"""
    if ENVIRONMENT != "production":
        logger.debug(message, extra=kwargs)

def log_info(message: str, **kwargs: Any) -> None:
    """Log info message with context"""
    logger.info(message, extra=kwargs)

def log_warning(message: str, **kwargs: Any) -> None:
    """Log warning message with context"""
    logger.warning(message, extra=kwargs)

def log_error(message: str, **kwargs: Any) -> None:
    """Log error message with context"""
    logger.error(message, extra=kwargs)
