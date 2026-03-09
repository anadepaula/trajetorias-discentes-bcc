from loguru import logger
import sys

logger.remove()

logger_format = (
    "{time:YYYY-MM-DD HH:mm:ss} "
    "| <level>{level: <8}</level> "
    "| <level>{message}</level> "
    "({function}, {file}:{line})"
)

# Console output with custom format and colors
logger.add(
    sys.stderr,
    format=logger_format,
    level="INFO",
    colorize=True,
)

# File output with rotation and retention
logger.add(
    "file.log",
    format=logger_format,
    level="DEBUG",
    rotation="10 MB",
    retention="1 week",
    compression="zip",
)
