# -*- coding: utf-8 -*-
"""."""
# -*- coding: utf-8 -*-
import logging

from google.cloud import logging as cloud_logging
from clouddeploy_extension.settings import settings

LOGGING_CONFIG_DICT = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s - [%(levelname)s] - %(name)s: %(message)s"},
    },
    "handlers": {
        "default": {
            "level": settings.log_level,
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["default"],
            "level": settings.log_level,
            "propagate": True,
        },
        "uvicorn": {
            "handlers": ["default"],
            "level": settings.log_level,
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["default"],
            "level": "WARNING",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["default"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}


def setup_cloud_logging() -> None:
    """
    setup_cloud_logging configures the app to use structured logging for improved
    log entries in Google Cloud Logging.
    """
    package_logger = logging.getLogger("")
    for handler in package_logger.handlers:
        package_logger.removeHandler(handler)
    client = cloud_logging.Client()
    client.setup_logging(log_level=getattr(logging, settings.log_level))
