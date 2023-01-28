# -*- coding: utf-8 -*-
"""A Cloud Deploy app responder application."""
import logging
import os
from logging import config as logging_config
from typing import Any, Dict

from fastapi import Request
from fastapi.responses import JSONResponse

from cloud_deploy_notifier.config import settings
from cloud_deploy_notifier.logging import LOGGING_CONFIG_DICT, setup_cloud_logging
from cloud_deploy_notifier.notifier import Notifier

logger = logging.getLogger(__name__)


async def setup_logging() -> None:
    """
    setup_logging sets up structured logging when running on Cloud Run.
    """
    logging_config.dictConfig(LOGGING_CONFIG_DICT)
    # TODO(brandonjbjelland): the K_SERVICE env var should only be present when running
    # as a knative service - so not local. Find a better way to determine this.
    if os.environ.get("K_SERVICE"):
        setup_cloud_logging()


async def get_healthz() -> JSONResponse:
    """A simple healthcheck endpoint."""
    return JSONResponse(
        content={"status": "OK"},
    )


async def index(request: Request) -> JSONResponse:
    """
    index is the main entrypoint for pubsub-generated Cloud Deploy event.
    """
    body: Dict[str, Any] = await request.json()
    try:
        notifier: Notifier = Notifier(
            request_json=body,
        )
    except Exception as err:
        logger.critical("json payload could not be parsed: %s", err)
        logger.critical(body)
        return JSONResponse(
            content={"status": "Failed to parse json payload"},
            status_code=400,
        )
    notifier.skip_update_actions()
    notifier.set_message_type()
    notifier.pipeline_has_notifier_annotation()
    if not notifier.annotation_exists_on_pipeline:
        logger.info(
            "annotation (%s) for notifier %s was not found on this pipeline",
            notifier.annotation,
            settings.app_name,
        )
        return JSONResponse(content={"status": "annotation not found"})

    config = notifier.get_config_from_secret(
        secret_id=notifier.pipeline.annotations[notifier.annotation]  # type: ignore
    )
    if not config:
        return JSONResponse(content={"status": "No secret found"})

    logger.info("successfully fetched config from secret manager: %s", config)
    return JSONResponse(content={"status": "OK"})
