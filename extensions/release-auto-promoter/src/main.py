# -*- coding: utf-8 -*-
"""A Cloud Deploy Extension to automatically promote releases as they succeed in pipelines."""
import logging
import os
from logging import config as logging_config
from typing import Any, Dict

from clouddeploy_extension.log_config import LOGGING_CONFIG_DICT, setup_cloud_logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.extension import Extension
from src.settings import settings

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
        extension = Extension(request_json=body, annotation=settings.annotation)
    except Exception as err:
        logger.critical("json payload could not be parsed: %s", err)
        logger.critical(body)
        return JSONResponse(
            content={"status": "Failed to parse json payload"},
            status_code=400,
        )
    return extension.execute()
