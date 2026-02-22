"""
Logging configuration for the application
"""
import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings

# Remove default logger
logger.remove()

# Add custom logging format
logger.add(
    sys.stderr,
    format=settings.LOG_FORMAT,
    level=settings.LOG_LEVEL,
    backtrace=True,
    diagnose=True,
    enqueue=True
)

# Add file logging
log_file = Path("logs/cogniflow.log")
log_file.parent.mkdir(exist_ok=True)

logger.add(
    log_file,
    rotation="500 MB",
    retention="10 days",
    compression="zip",
    format=settings.LOG_FORMAT,
    level=settings.LOG_LEVEL,
    backtrace=True,
    diagnose=True,
    enqueue=True
)

# Catch unhandled exceptions
@logger.catch
def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        
    logger.error(
        "Uncaught exception:",
        exc_info=(exc_type, exc_value, exc_traceback)
    )

sys.excepthook = handle_exception

# Export logger
__all__ = ["logger"]