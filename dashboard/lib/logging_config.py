import logging.config
import os
from pathlib import Path

LOG_DIR = Path("/var/log/thalasshome")


def setup_logging(testing=False):
    """Configure logging for the application"""
    if not LOG_DIR.exists() and not testing:
        os.makedirs(LOG_DIR, exist_ok=True)

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG" if testing else "INFO",
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": (
                    LOG_DIR / "thalasshome.log" if not testing else "/tmp/test.log"
                ),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": (
                    LOG_DIR / "error.log" if not testing else "/tmp/test_error.log"
                ),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console", "file", "error_file"],
                "level": "DEBUG" if testing else "INFO",
                "propagate": True,
            },
            "dashboard": {
                "handlers": ["console", "file", "error_file"],
                "level": "DEBUG" if testing else "INFO",
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(config)
