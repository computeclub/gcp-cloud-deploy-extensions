# -*- coding: utf-8 -*-
from __future__ import annotations

from clouddeploy_extension.settings import BaseExtensionSettings


class ExtensionSettings(BaseExtensionSettings):

    """
    Application specific settings.
    """

    app_name: str = "image-tagger"


settings = ExtensionSettings()  # type: ignore
