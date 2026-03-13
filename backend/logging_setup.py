import logging
import os
from dotenv import load_dotenv

load_dotenv()

def setup_logger(name: str, log_file: str = None, level: int = None):
    """
    Create or return a configured logger.
    Avoid adding duplicate handlers if the logger already has handlers.
    """
    if level is None:
        level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper())
    if log_file is None:
        log_file = os.getenv("LOG_FILE", "server.log")

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File handler
    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console handler (helpful during development)
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger