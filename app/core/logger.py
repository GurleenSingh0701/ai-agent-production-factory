import logging
import sys
from datetime import datetime
from app.core.config import settings

def setup_logger(name: str = "AI_FACTORY"):
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Formatter for clean, readable logs
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Optional: File Handler for persistent logs
        try:
            file_handler = logging.FileHandler("factory.log")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Could not create log file: {e}")

    return logger

# Initialize global logger
logger = setup_logger()
