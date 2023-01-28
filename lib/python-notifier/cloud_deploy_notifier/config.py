# -*- coding: utf-8 -*-
"""config contains app configurations."""
import logging
import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Application settings.
    """

    # TODO(brandonjbjelland): does this break?
    app_name: str
    log_level: str = os.environ.get("LOG_LEVEL") or logging.getLevelName(
        logging.getLogger("uvicorn.error").level
    )

    class Config:
        """Enables dotenv files to be read at startup."""

        env_file = ".env"


settings = Settings()  # type: ignore
