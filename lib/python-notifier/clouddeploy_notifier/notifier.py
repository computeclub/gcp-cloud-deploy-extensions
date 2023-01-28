# -*- coding: utf-8 -*-
import abc
import logging
import os
from typing import Any, Dict, Optional, Tuple

from clouddeploy_notifier.types import PubSubEnvelope
from google.cloud import deploy, secretmanager
from google.cloud.deploy_v1.types import DeliveryPipeline, GetDeliveryPipelineRequest


logger = logging.getLogger(__name__)


class BaseNotifier(abc.ABC):
    def __init__(self, request_json: Dict[str, Any], skip_updates: bool = True) -> None:
        self.envelope = PubSubEnvelope(**request_json)

    def action(self):
        raise NotImplementedError

    # TODO: is this necessary?
    def set_message_type(self):
        if hasattr(self.envelope.message.attributes, "Rollout"):
            self.message_type = "Approvals"
        elif hasattr(self.envelope.message.attributes, "PhaseId"):
            self.message_type = "Operations"
        self.message_type = "Resources"

    def pipeline_has_notifier_annotation(
        self,
        pipeline_id: str,
    ) -> Tuple[bool, Optional[DeliveryPipeline]]:
        """
        pipeline_has_notifier_annotation.
        """
        logger.debug("getting pipeline")
        # TODO(brandonjbjelland): try the Async clients
        deploy_client = deploy.CloudDeployClient()
        pipeline_request = GetDeliveryPipelineRequest(name=pipeline_id)
        try:
            pipeline: DeliveryPipeline = deploy_client.get_delivery_pipeline(
                pipeline_request
            )  # TODO(brandonjbjelland): catch specific exception
        except Exception as err:
            logger.critical(err)
            return (False, None)

        if os.environ["NOTIFIER_CONFIG_PIPELINE_ANNOTATION"] in pipeline.annotations:
            return (True, pipeline)
        return (False, pipeline)

    def get_pipeline_id(self) -> str:
        """get_pipeline_id."""
        logger.debug("getting pipeline_id from %s", self.envelope.message.attributes)
        if hasattr(self.envelope.message.attributes, "Rollout"):
            return self.envelope.message.attributes.Rollout.rsplit("/", 4)[0]

        if (
            hasattr(self.envelope.message.attributes, "Resource")
            and "/deliveryPipelines/" in attributes.Resource
        ):
            delimeter = "/deliveryPipelines/"
            return (
                self.envelope.message.attributes.Resource.split(delimeter)[0]
                + delimeter
                + self.envelope.message.attributes.Resource.split(delimeter)[1].split(
                    "/"
                )[0]
            )

        logger.critical("failed to get pipeline_id from: %s", str(attributes))
        raise Exception("No pipeline_id found.")
