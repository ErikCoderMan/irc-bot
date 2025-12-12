import logging

# Path to log file
from core.paths import LOG_FILE

# Create a custom logger
logger = logging.getLogger("IRC_Bot")
logger.setLevel(logging.DEBUG)  # Capture all log levels

# Console handler for terminal output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Adjust level for console

# File handler to save all logs
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)  # Capture everything in file

# Define log message format
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)


# Helper functions for convenience
def log_info(msg: str):
    logger.info(msg)


def log_warning(msg: str):
    logger.warning(msg)


def log_error(msg: str):
    logger.error(msg)


def log_debug(msg: str):
    logger.debug(msg)
