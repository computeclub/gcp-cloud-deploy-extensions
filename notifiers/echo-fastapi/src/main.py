# -*- coding: utf-8 -*-
"""This is an example Cloud Deploy app responder."""
import json
import logging
import os
from logging import config as logging_config
from typing import Any, Dict, Optional, Tuple

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from google.api_core.exceptions import PermissionDenied
from google.cloud import deploy, secretmanager
from google.cloud.deploy_v1.types import DeliveryPipeline, GetDeliveryPipelineRequest
from google.cloud.secretmanager_v1.types import AccessSecretVersionRequest

from src.logging import LOGGING_CONFIG_DICT, setup_cloud_logging
from src.settings import settings
from src.types import PubSubEnvelope

logger = logging.getLogger(__name__)


app: FastAPI = FastAPI()


@app.on_event("startup")
async def setup_logging() -> None:
    """
    setup_logging sets up structured logging when running on Cloud Run.
    """
    logging_config.dictConfig(LOGGING_CONFIG_DICT)
    # the K_SERVICE env var should only be present when running as a knative service
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
        envelope = PubSubEnvelope(**body)
        logger.debug("message originated from: %s", envelope.subscription)
    except Exception as err:
        logger.critical("json payload could not be parsed: %s", err)
        logger.critical(body)
        return JSONResponse(
            content={"status": "Failed to parse json payload"},
            status_code=400,
        )

    # TODO(bjb): I think these are Updates to Resources but verify
    if envelope.message.attributes.Action == "Update":
        logger.info("skipping message with Update action")
        return JSONResponse(content={"status": "Update actions are a no-op"})
    pipeline_id: str = get_pipeline_id(attributes=envelope.message.attributes)

    if hasattr(envelope.message.attributes, "Rollout"):
        message_type = "Approvals"
    elif hasattr(envelope.message.attributes, "PhaseId"):
        message_type = "Operations"
    else:
        message_type = "Resources"

    logger.debug("found a %s message", message_type)
    (notifier_annotation_exists, pipeline) = pipeline_has_notifier_annotation(
        pipeline_id
    )
    if not notifier_annotation_exists:
        logger.info(
            "annotation (%s) for notifier %s was not found on this pipeline",
            {os.environ["ANNOTATION"]},
            settings.app_name,
        )
        return JSONResponse(content={"status": "annotation not found"})

    config = get_config_from_secret(
        secret_id=pipeline.annotations[os.environ["ANNOTATION"]]  # type: ignore
    )
    if not config:
        return JSONResponse(content={"status": "No secret found"})

    logger.info("successfully fetched config from secret manager: %s", config)
    return JSONResponse(content={"status": "OK"})


def get_pipeline_id(attributes) -> str:
    """get_pipeline_id."""
    logger.debug("getting pipeline_id from %s", attributes)
    if hasattr(attributes, "Rollout"):
        return attributes.Rollout.rsplit("/", 4)[0]

    if hasattr(attributes, "Resource") and "/deliveryPipelines/" in attributes.Resource:
        delimeter = "/deliveryPipelines/"
        return (
            attributes.Resource.split(delimeter)[0]
            + delimeter
            + attributes.Resource.split(delimeter)[1].split("/")[0]
        )

    logger.critical("failed to get pipeline_id from: %s", str(attributes))
    raise Exception("No pipeline_id found.")


def pipeline_has_notifier_annotation(
    pipeline_id: str,
) -> Tuple[bool, Optional[DeliveryPipeline]]:
    """
    pipeline_has_notifier_annotation.
    """
    logger.debug("getting pipeline")
    deploy_client = deploy.CloudDeployClient()
    pipeline_request = GetDeliveryPipelineRequest(name=pipeline_id)
    try:
        pipeline: DeliveryPipeline = deploy_client.get_delivery_pipeline(
            pipeline_request
        )  # TODO(bjb): catch specific exception
    except Exception as err:
        logger.critical(err)
        return (False, None)

    if os.environ["ANNOTATION"] in pipeline.annotations:
        return (True, pipeline)
    return (False, pipeline)


def get_config_from_secret(secret_id: str) -> Dict[str, Any]:
    """
    get_config_from_secret.
    """
    secret_path = f"{secret_id}/versions/latest"
    logger.debug("getting config from secret %s", secret_path)
    secretmanager_client = secretmanager.SecretManagerServiceClient()
    secret_version_request = AccessSecretVersionRequest(name=secret_path)
    try:
        secret_payload = secretmanager_client.access_secret_version(
            request=secret_version_request
        ).payload.data.decode("utf-8")
    except PermissionDenied as err:
        logger.critical(
            "access_secret_version() failed to fetch and decode the secret: %s", err
        )
        return {}

    try:
        secret_contents = json.loads(secret_payload)
    except json.decoder.JSONDecodeError as err:
        logger.critical("secret could not be loaded as json: %s", err)
        return {}

    if "enabled" not in secret_contents or not secret_contents["enabled"]:
        logger.info(
            'A secret founds  but "enabled" was either absent or set false: %s',
            secret_path,
        )
        return {}

    return secret_contents
