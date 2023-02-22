# -*- coding: utf-8 -*-
"""config contains logging and app configurations."""
from __future__ import annotations
from clouddeploy_extension.settings import BaseExtensionSettings


class ExtensionSettings(BaseExtensionSettings):
    """
    Application settings.
    """

    app_name: str = "echo-fastapi"


settings = ExtensionSettings()  # type: ignore
