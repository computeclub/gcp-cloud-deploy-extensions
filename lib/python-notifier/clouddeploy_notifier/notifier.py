# -*- coding: utf-8 -*-
import abc
import json
import logging
from typing import Any, Dict, Optional
from clouddeploy_notifier.exceptions import UnknownMessageType, UnkownPipeline

from clouddeploy_notifier.types import (
    ApprovalsAttributes,
    OperationsAttributes,
    PubSubEnvelope,
    ResourcesAttributes,
)
from fastapi.responses import JSONResponse
from google.cloud import deploy, secretmanager
from google.api_core.exceptions import PermissionDenied, NotFound
from google.cloud.deploy_v1.types import DeliveryPipeline, GetDeliveryPipelineRequest
from google.cloud.secretmanager_v1.types import AccessSecretVersionRequest


logger = logging.getLogger(__name__)


class BaseNotifier(abc.ABC):
    """
    BaseNotifier is a base class providing common methods for notifiers
    to use.
    """

    def __init__(self, request_json: Dict[str, Any], annotation: str) -> None:
        self.pipeline = None
        self.annotation = annotation
        self.envelope = PubSubEnvelope(**request_json)
        self.attributes = self.envelope.message.attributes

    def action(self, config: Dict[str, Any], **kwargs):
        """
        action is the core notifier action to be implemented by a library
        consumer.
        """
        raise NotImplementedError

    def execute(self, **kwargs) -> JSONResponse:
        """
        execute is a high-level workflow executor to perform the most common
        notifier workflow:
        1. determine the pipeline that sent the notification
        2. parse that pipeline's configuration checking for the notifier's annotation
        3. use the annotation value to lookup a secret in secret manager
        4. use the decrypted secret contents to execute the user-defined action()
        """
        try:
            self.pipeline = self.get_pipeline(
                pipeline_id=self.get_pipeline_id(attributes=self.attributes)
            )
            if not self.pipeline:
                logger.debug(
                    "insufficent permissions to get pipeline: %s", self.pipeline
                )
                return JSONResponse(content={"status": "pipeline not found"})

        except Exception as err:
            logger.critical("failed to get pipeline: %s", err)
            return JSONResponse(content={"status": "pipeline not found"})

        if not self.annotation in self.pipeline.annotations:
            logger.debug("annotation not present on the pipeline: %s", self.pipeline)
            return JSONResponse(content={"status": "annotation not found"})

        config = self.get_config_from_secret(
            secret_id=self.pipeline.annotations[self.annotation]
        )
        if not config:
            logger.debug("configuration was either empty or set enabled to false")
            return JSONResponse(content={"status": "notifier disabled"})

        try:
            self.action(config=config, kwargs=kwargs)
        except Exception as err:
            logger.critical(err)
            return JSONResponse(
                content={"status": "failed to execute the notifier action"},
            )

        return JSONResponse(content={"status": "executed successfully"})

    @staticmethod
    def get_message_type(
        attributes: ApprovalsAttributes | OperationsAttributes | ResourcesAttributes,
    ) -> str:
        """
        get_message_type takes the attributes of a message and determines
        the PubSub topic source.
        """
        return attributes.__class__.__name__.split(".")[-1].removesuffix("Attributes")

    @staticmethod
    def get_pipeline(pipeline_id: str) -> DeliveryPipeline | None:
        """
        get_pipeline takes a pipeline by ID and fetches the matching
        DeliveryPipeline object.
        """
        deploy_client = deploy.CloudDeployClient()
        pipeline_request = GetDeliveryPipelineRequest(name=pipeline_id)
        try:
            return deploy_client.get_delivery_pipeline(pipeline_request)
        except PermissionDenied as err:
            logger.critical(err)
            return None

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
        raise UnkownPipeline("No pipeline_id found.")

    @staticmethod
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
            logger.warning("failed to decode the secret: %s", err)
            return {}
        except NotFound as err:
            logger.warning("No secret version was found: %s", err)
            return {}

        try:
            secret_contents = json.loads(secret_payload)
        except json.decoder.JSONDecodeError as err:
            logger.critical("secret could not be loaded as json: %s", err)
            return {}

        if "enabled" not in secret_contents or secret_contents["enabled"] == False:
            logger.info(
                "This notifier is not enabled per the configuration: %s",
                secret_path,
            )
            return {}

        return secret_contents

    @staticmethod
    def get_release_id(
        attributes: ApprovalsAttributes | OperationsAttributes | ResourcesAttributes,
    ) -> Optional[str]:
        """
        get_release_id derives the release_id from attributes when possible. If
        successfully determined, the format is:
        projects/{project_id}/locations/{location_name}/deliveryPipelines/{pipeline_name}/releases/{release_name}.
        """
        pass
