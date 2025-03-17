import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: int = logging.INFO,
    log_file: Optional[str] = "logs/sitechat.log"
) -> logging.Logger:
    """
    Configure application-wide logging with both file and console handlers.
    
    Args:
        log_level: The logging level to use (default: logging.INFO)
        log_file: Path to the log file (default: logs/sitechat.log)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist and log_file is specified
    if log_file:
        log_dir = Path(log_file).parent
        log_dir.mkdir(exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    if log_file:
        # Setup file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create and configure application logger
    logger = logging.getLogger("sitechat")
    logger.setLevel(log_level)
    
    return logger


def get_logger(name: str = "sitechat") -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: The name for the logger (default: sitechat)
    
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)
