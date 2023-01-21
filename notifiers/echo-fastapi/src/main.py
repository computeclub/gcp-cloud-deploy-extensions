# -*- coding: utf-8 -*-
"""This is an example Cloud Deploy app responder."""
import json
import logging
import sys
from typing import Any, Dict, Optional, Tuple
import os

from fastapi import FastAPI, Response, Request
from google.cloud import logging as cloud_logging
from google.cloud import secretmanager
from google.cloud import deploy
from google.cloud.deploy_v1.types import (
    GetDeliveryPipelineRequest,
    DeliveryPipeline,
)
from google.cloud.secretmanager_v1.types import (
    GetSecretVersionRequest,
)

from src.types import PubSubEnvelope

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()


@app.on_event("startup")
async def setup_logging() -> None:
    """
    setup_logging sets up structured logging when running on Cloud Run.
    """
    # TODO(brandonjbjelland): the K_SERVICE env var should only be present when running
    # as a knative service - so not local. Find a better way to determine this.
    if os.environ.get("K_SERVICE"):
        package_logger = logging.getLogger("")
        for handler in package_logger.handlers:
            package_logger.removeHandler(handler)
        client = cloud_logging.Client()
        client.setup_logging()


@app.get("/healthz")
async def get_healthz() -> Response:
    """A simple healthcheck endpoint."""
    return Response(
        content=json.dumps({"status": "OK"}),
    )


@app.post("/")
async def index(request: Request) -> Response:
    """
    index is the main entrypoint for pubsub-generated Cloud Deploy event.
    """
    body: Dict[str, Any] = await request.json()
    # TODO(brandonjbjelland): how to control log level?
    logger.debug("debug")
    try:
        envelope = PubSubEnvelope(**body)
    except Exception as err:
        logger.critical("payload could not be parsed")
        logger.critical(request)
        logger.critical(err)
        sys.exit(1)

    pipeline_id = get_pipeline_id(attributes=envelope.message.attributes)

    if hasattr(envelope.message.attributes, "Rollout"):
        message_type = "Approvals"
    elif hasattr(envelope.message.attributes, "PhaseId"):
        message_type = "Operations"
    else:
        message_type = "Resources"

    logger.info(f"found a {message_type} message")
    (notifier_enabled, pipeline) = notifier_is_enabled(pipeline_id)
    if not notifier_enabled:
        return Response(content=json.dumps({"status": "notifier not enabled"}))

    config = get_config_from_secret(
        secret_id=pipeline.annotations[
            os.environ["DEPLOYER_CONFIG_PIPELINE_ANNOTATION"]
        ]
    )
    if not config:
        return Response(content=json.dumps({"status": "no secret found"}))

    logger.info(f"successfully fetched config from secret manager: {config}")
    return Response(content=json.dumps({"status": "OK"}))


def get_pipeline_id(attributes) -> str:
    """get_pipeline_id."""
    if hasattr(attributes, "Rollout"):
        return attributes.Rollout.rsplit("/", 4)[0]
    elif hasattr(attributes, "Resource"):
        delimeter = "/deliveryPipelines/"
        return (
            attributes.Resource.split()[0]
            + delimeter
            + attributes.Resource.split(delimeter)[1].split("/")[0]
        )
    else:
        logger.critical("failed to get pipeline_id from:")
        logger.critical(attributes)
        raise Exception("No pipeline_id found.")


def notifier_is_enabled(
    pipeline_id: str,
) -> Tuple[bool, Optional[DeliveryPipeline]]:
    """
    notifier_is_enabled.
    """
    logger.info("getting pipeline")
    # TODO(brandonjbjelland): try the Async clients
    deploy_client = deploy.CloudDeployClient()
    pipeline_request = GetDeliveryPipelineRequest(name=pipeline_id)
    try:
        pipeline: DeliveryPipeline = deploy_client.get_delivery_pipeline(
            pipeline_request
        )
    # TODO(brandonjbjelland): catch specific exception
    except Exception as err:
        logger.critical(err)
        return (False, None)

    if os.environ["DEPLOYER_CONFIG_PIPELINE_ANNOTATION"] in pipeline.annotations:
        return (True, pipeline)
    return (False, pipeline)


def get_config_from_secret(secret_id: str) -> str:
    """
    get_config_from_secret.
    """
    logger.info("getting config from secret")
    secretmanager_client = secretmanager.SecretManagerServiceClient()
    secret_version_request = GetSecretVersionRequest(
        name=f"{secret_id}/versions/latest"
    )
    try:
        secret_version = secretmanager_client.get_secret_version(
            request=secret_version_request
        )
        logger.info(secret_version.__dict__)
        return secret_version.name
    # TODO(brandonjbjelland): catch specific exception
    except Exception as err:
        logger.critical(err)
        return ""
