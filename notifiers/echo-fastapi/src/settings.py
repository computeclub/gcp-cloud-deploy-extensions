# -*- coding: utf-8 -*-
"""config contains logging and app configurations."""
import logging

from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Application settings.
    """

    app_name: str = "echo-fastapi"
    log_level: str = logging.getLevelName(logging.getLogger("uvicorn.error").level)

    class Config:
        """Enables dotenv files to be read at startup."""

        env_file = ".env"


settings = Settings()  # type: ignore
