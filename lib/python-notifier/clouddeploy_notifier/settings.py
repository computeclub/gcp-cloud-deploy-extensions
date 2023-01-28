# -*- coding: utf-8 -*-
"""config contains logging and app configurations."""
import logging

from pydantic import BaseSettings


class BaseNotifierSettings(BaseSettings):
    """
    Application settings.
    """

    app_name: str
    log_level: str = logging.getLevelName(logging.getLogger("uvicorn.error").level)

    class Config:
        """Enables dotenv files to be read at startup."""

        env_file = ".env"
