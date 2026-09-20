"""
Centralized colorized logger module for Encor.
Provides ANSI color-coded loggers for FastAPI and engine subsystems.
"""

import logging
import sys

# ANSI Color codes for Windows/Linux terminals
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_BLUE = "\033[34m"
COLOR_MAGENTA = "\033[35m"
COLOR_CYAN = "\033[36m"
COLOR_RED = "\033[31m"

class ColorFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: f"{COLOR_BLUE}[DEBUG]{COLOR_RESET} %(asctime)s - %(name)s - %(message)s",
        logging.INFO: f"{COLOR_GREEN}[INFO]{COLOR_RESET} %(asctime)s - {COLOR_BOLD}%(name)s{COLOR_RESET} - %(message)s",
        logging.WARNING: f"{COLOR_YELLOW}[WARN]{COLOR_RESET} %(asctime)s - %(name)s - %(message)s",
        logging.ERROR: f"{COLOR_RED}[ERROR]{COLOR_RESET} %(asctime)s - %(name)s - %(message)s",
        logging.CRITICAL: f"{COLOR_RED}{COLOR_BOLD}[CRITICAL]{COLOR_RESET} %(asctime)s - %(name)s - %(message)s",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self._fmt)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)

def get_logger(name: str = "encor") -> logging.Logger:
    """Return a configured colorized logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(ColorFormatter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger

# Pre-instantiated loggers for subsystems
main_logger = get_logger("encor.main")
auth_logger = get_logger("encor.auth")
discovery_logger = get_logger("encor.discovery")
engagement_logger = get_logger("encor.engagement")
safety_logger = get_logger("encor.safety")
