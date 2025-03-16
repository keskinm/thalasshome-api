import logging.config


def setup_logging(testing=False):
    """Configure logging for the application"""
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
            }
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console"],
                "level": "DEBUG" if testing else "INFO",
                "propagate": True,
            },
            "dashboard": {
                "handlers": ["console"],
                "level": "DEBUG" if testing else "INFO",
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(config)
