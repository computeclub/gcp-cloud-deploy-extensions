# -*- coding: utf-8 -*-
"""This is an example Cloud Deploy app responder."""
import json
import logging
from typing import Any, Dict

from fastapi import FastAPI, Response, Request
from google.cloud import logging as cloud_logging

# import secretmanager
# import clouddeploy
from src.types import PubSubEnvelope

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()


@app.on_event("startup")
async def setup_logging() -> None:
    """."""
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
    print('just a print')
    logger.critical('critical')
    logger.warning('warning')
    logger.info('info')
    logger.debug('debug')
    logger.info(body)
    envelope = PubSubEnvelope(**body)
    if hasattr(envelope.message.attributes, "Rollout"):
        message_type = "Approval"
        # Action == 'Rejected' # notify team
        # Action == 'Required' # DM
    elif hasattr(envelope.message.attributes, "PhaseId"):
        message_type = "Operations"
        # Action=='Start' && JobType=='Deploy' # notify team
        # Action=='Failure' && JobType=='Verify' # notify team
        # Action=='Succeed' && JobType=='Verify' && TargetId=='.*prod$' # notify
        # Action=='Succeed' && JobType=='Verify' && TargetId=='.*(dev|training)$' # auto promote
        # Action=='Succeed' && JobType=='Verify' # tag
        # Action==Any # record a metric for duration and success value
    else:
        message_type = "Resources"
        # OOB: notify if a release sits unpromoted in some stage

    # TODO(brandonjbjelland): iterate over all pipelines found in the project.
    # identify those having the DEPLOYER_CONFIG_PIPELINE_ANNOTATION annotation

    logger.info("%s - %s", message_type, str(request.__dict__))
    return Response(content=json.dumps({"status": "OK"}))
