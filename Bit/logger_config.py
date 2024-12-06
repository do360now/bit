import logging
from logging.handlers import RotatingFileHandler
import os

# Determine the desired log level from the environment variable.
# Defaults to INFO if not provided.
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Create and configure the main logger.
logger = logging.getLogger("trading_bot")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

# Console handler: logs to stdout, useful for real-time monitoring.
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# File handler: Rotating file handler for persistent logging.
# Keeps logs manageable by limiting file size and maintaining backups.
log_file = os.getenv("LOG_FILE", "trading_bot.log")
log_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(file_formatter)
logger.addHandler(log_handler)

# Disable propagation to avoid log duplication if other loggers are configured.
logger.propagate = False
