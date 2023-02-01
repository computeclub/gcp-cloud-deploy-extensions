# -*- coding: utf-8 -*-
import logging
import uuid
from typing import Any, Dict

from clouddeploy_notifier.notifier import BaseNotifier
from google.cloud import deploy
from google.cloud.deploy_v1.types import CreateRolloutRequest, Rollout

logger = logging.getLogger(__name__)


class Notifier(BaseNotifier):
    """Notifier implements action for this use-case."""

    def action(self, config: Dict[str, Any]):
        """."""
        logging.debug("executing the action")

        completed_stage_index = [
            idx
            for idx, stage in enumerate(self.pipeline.serial_pipeline.stages)
            if stage.target_id == self.attributes.TargetId
        ]

        if (
            completed_stage_index
            and len(self.pipeline.serial_pipeline.stages)
            == completed_stage_index[0] + 1
        ):
            logger.info(
                "Rollout succeeded on the final stage. Nowhere to promote further. Exiting."
            )
            return None

        target_id = self.pipeline.serial_pipeline.stages[
            completed_stage_index[0] + 1
        ].target_id

        rollout = Rollout()
        rollout.target_id = target_id
        rollout.description = "A rollout created by release-auto-promoter"

        request = CreateRolloutRequest(
            parent=f"projects/{self.attributes.ProjectNumber}/locations/{self.attributes.Location}/deliveryPipelines/{self.attributes.DeliveryPipelineId}/releases/{self.attributes.ReleaseId}",
            rollout_id=f"{self.attributes.ReleaseId}-to-{target_id}-{str(uuid.uuid4())[0:8]}",
            rollout=rollout,
        )

        deploy_client = deploy.CloudDeployClient()
        deploy_client.create_rollout(request=request)
        logger.info("The release has been successfully auto-promoted")
