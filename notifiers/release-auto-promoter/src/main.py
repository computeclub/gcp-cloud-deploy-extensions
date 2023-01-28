# -*- coding: utf-8 -*-
"""A Cloud Deploy Notifier to automatically promote releases as they succeed in pipelines."""
import logging
from logging import config as logging_config
import os
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from google.api_core.exceptions import PermissionDenied
from google.cloud import deploy, secretmanager
from google.cloud.deploy_v1.types import DeliveryPipeline, GetDeliveryPipelineRequest
from google.cloud.secretmanager_v1.types import AccessSecretVersionRequest

from clouddeploy_notifier.logging import LOGGING_CONFIG_DICT, setup_cloud_logging
from clouddeploy_notifier.types import PubSubEnvelope
from src.settings import settings
from src.notifier import Notifier

logger = logging.getLogger(__name__)
app: FastAPI = FastAPI()


@app.on_event("startup")
async def setup_logging() -> None:
    """
    setup_logging sets up structured logging when running on Cloud Run.
    """
    logging_config.dictConfig(LOGGING_CONFIG_DICT)
    if os.environ.get("K_SERVICE"):
        setup_cloud_logging()


@app.get("/healthz")
async def get_healthz() -> JSONResponse:
    """A simple healthcheck endpoint."""
    return JSONResponse(
        content={"status": "OK"},
    )


@app.post("/")
async def index(request: Request) -> JSONResponse:
    """
    index is the main entrypoint for pubsub-generated Cloud Deploy event.
    """
    body: Dict[str, Any] = await request.json()
    try:
        notifier = Notifier(body)
    except Exception as err:
        logger.critical("json payload could not be parsed: %s", err)
        logger.critical(body)
        return JSONResponse(
            content={"status": "Failed to parse json payload"},
            status_code=400,
        )
    pipeline_id: str = notifier.get_pipeline_id()
    (notifier_annotation_exists, pipeline) = notifier.pipeline_has_notifier_annotation(
        pipeline_id
    )
