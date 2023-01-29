# -*- coding: utf-8 -*-
"""config contains logging and app configurations."""
import logging
import os

from pydantic import BaseSettings


class BaseNotifierSettings(BaseSettings):
    """
    Application settings.
    """

    annotation: str
    log_level: str = logging.getLevelName(logging.getLogger("uvicorn.error").level)

    class Config:
        """Enables dotenv files to be read at startup."""

        env_file = ".env"


settings: BaseNotifierSettings = BaseNotifierSettings()
