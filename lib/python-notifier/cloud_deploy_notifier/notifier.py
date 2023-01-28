# -*- coding: utf-8 -*-
"""This is an example Cloud Deploy app responder."""
import abc
import json
import logging
import os
from typing import Any, Dict

from fastapi.responses import JSONResponse
from google.api_core.exceptions import PermissionDenied
from google.cloud import deploy, secretmanager
from google.cloud.deploy_v1.types import DeliveryPipeline, GetDeliveryPipelineRequest
from google.cloud.secretmanager_v1.types import AccessSecretVersionRequest

from src.types import PubSubEnvelope

logger = logging.getLogger(__name__)


class Notifier(abc.ABC):
    """."""

    def __init__(self, request_json: Dict[str, Any]) -> None:
        self.annotation_exists_on_pipeline: bool = False
        self.message_type: str = ""
        self.pipeline = None
        self.pipeline_id: str = ""
        self.annotation = os.environ["NOTIFIER_CONFIG_PIPELINE_ANNOTATION"]

        self.envelope = PubSubEnvelope(**request_json)
        self.subscription = self.envelope.subscription
        self.pipeline_id = self.get_pipeline_id(
            attributes=self.envelope.message.attributes
        )

    @abc.abstractmethod
    def action(self):
        """The core action to be implemented and performed by Notifiers."""
        raise NotImplementedError

    # def

    def skip_update_actions(self):
        """."""
        if self.envelope.message.attributes.Action == "Update":
            logger.info("skipping message with Update action")
            return JSONResponse(content={"status": "Update actions are a no-op"})

    @staticmethod
    def get_pipeline_id(attributes) -> str:
        """get_pipeline_id."""
        logger.debug("getting pipeline_id from %s", attributes)
        if hasattr(attributes, "Rollout"):
            return attributes.Rollout.rsplit("/", 4)[0]

        if (
            hasattr(attributes, "Resource")
            and "/deliveryPipelines/" in attributes.Resource
        ):
            delimeter = "/deliveryPipelines/"
            return (
                attributes.Resource.split(delimeter)[0]
                + delimeter
                + attributes.Resource.split(delimeter)[1].split("/")[0]
            )

        logger.critical("failed to get pipeline_id from: %s", str(attributes))
        raise Exception("No pipeline_id found.")

    def set_message_type(
        self,
    ):
        """set_message_type."""
        if hasattr(self.envelope.message.attributes, "Rollout"):
            self.message_type = "Approvals"
        elif hasattr(self.envelope.message.attributes, "PhaseId"):
            self.message_type = "Operations"
        else:
            self.message_type = "Resources"
        logger.debug("found a %s message", self.message_type)

    def pipeline_has_notifier_annotation(
        self,
    ) -> None:
        """
        pipeline_has_notifier_annotation.
        """
        logger.debug("getting pipeline")
        # TODO(brandonjbjelland): try the Async clients
        deploy_client = deploy.CloudDeployClient()
        pipeline_request = GetDeliveryPipelineRequest(name=self.pipeline_id)
        try:
            pipeline: DeliveryPipeline = deploy_client.get_delivery_pipeline(
                pipeline_request
            )
        # TODO(brandonjbjelland): catch specific exception
        except Exception as err:
            logger.critical(err)
            self.annotation_exists_on_pipeline = False

        if self.annotation in pipeline.annotations:
            self.annotation_exists_on_pipeline = True
            self.pipeline = pipeline

        self.annotation_exists_on_pipeline = False

    def get_config_from_secret(self, secret_id: str) -> Dict[str, Any]:
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
