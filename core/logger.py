import logging
from core.paths import LOG_FILE
from core.config import settings

# Read log levels from settings, fallback to defaults
console_level = getattr(logging, settings.get("log", {}).get("console_level", "INFO").upper(), logging.INFO)
file_level = getattr(logging, settings.get("log", {}).get("file_level", "DEBUG").upper(), logging.DEBUG)

# Create a custom logger
logger = logging.getLogger("IRC_Bot")
logger.setLevel(logging.DEBUG)  # Capture all levels, handlers filter individually

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(console_level)

# File handler
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setLevel(file_level)

# Formatter
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Helper functions for convenience
def log_debug(msg: str) -> None:
    logger.debug(msg)
    
def log_info(msg: str) -> None:
    logger.info(msg)

def log_warning(msg: str, exc: Exception | None = None) -> None:
    if exc:
        logger.warning(msg, exc_info=(type(exc), exc, exc.__traceback__))
    else:
        logger.warning(msg)

def log_error(msg: str, exc: Exception | None = None) -> None:
    if exc:
        logger.error(msg, exc_info=(type(exc), exc, exc.__traceback__))
    else:
        logger.error(msg)
