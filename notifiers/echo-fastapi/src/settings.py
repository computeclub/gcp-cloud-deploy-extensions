# -*- coding: utf-8 -*-
"""config contains logging and app configurations."""
from __future__ import annotations
from clouddeploy_notifier.settings import BaseNotifierSettings


class NotifierSettings(BaseNotifierSettings):
    """
    Application settings.
    """

    app_name: str = "echo-fastapi"


settings = NotifierSettings()  # type: ignore
