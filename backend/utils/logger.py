"""
PromptOptimizer Pro - Logging Utilities
Structured logging with JSON formatting for production
"""

import logging
import sys
from typing import Optional
from pythonjsonlogger import jsonlogger
from colorlog import ColoredFormatter
from ..config import Config


# Global logger cache
_loggers = {}


def setup_logging(name: str = "promptoptimizer", level: Optional[str] = None) -> logging.Logger:
    """
    Configure logging with appropriate formatters
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    if level is None:
        level = Config.LOG_LEVEL
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))
    
    # Use JSON formatter in production, colored formatter in development
    if Config.LOG_FORMAT == "json" and Config.is_production():
        formatter = jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # Colored output for development
        formatter = ColoredFormatter(
            fmt='%(log_color)s%(asctime)s - %(name)s - %(levelname)s%(reset)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get or create a logger instance (cached)
    
    Args:
        name: Logger name
        level: Optional log level override
    
    Returns:
        Logger instance
    """
    cache_key = f"{name}:{level or Config.LOG_LEVEL}"
    
    if cache_key not in _loggers:
        _loggers[cache_key] = setup_logging(name, level)
    
    return _loggers[cache_key]


class LoggerMixin:
    """Mixin class to add logging capabilities to any class"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return get_logger(self.__class__.__name__)


# Example usage in other modules:
# from utils.logger import get_logger
# logger = get_logger(__name__)
# logger.info("Message", extra={"user_id": 123, "action": "analyze"})