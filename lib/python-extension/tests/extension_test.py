# -*- coding: utf-8 -*-
from unittest.mock import patch
from google.api_core.exceptions import PermissionDenied, NotFound
from clouddeploy_extension.extension import BaseExtension

approval = {
    "message": {
        "attributes": {
            "Action": "Required",
            "DeliveryPipelineId": "some-id",
            "Location": "us-east4",
            "ProjectNumber": "957414832331",
            "ReleaseId": "release-0ba98f6",
            "Rollout": "projects/957414832331/locations/us-east4/deliveryPipelines/some-id/releases/release-0ba98f6/rollouts/release-0ba98f6-to-some-id-prod-0003",
            "RolloutId": "release-0ba98f6-to-some-id-prod-0003",
            "TargetId": "some-id-prod",
        },
        "messageId": "6641587404274478",
        "message_id": "6641587404274478",
        "publishTime": "2022-12-24T06:55:58.968Z",
        "publish_time": "2022-12-24T06:55:58.968Z",
    },
    "subscription": "projects/project-id/subscriptions/approvals-push",
}

base_extension = BaseExtension(
    request_json=approval,
    annotation="example",
)


class TestBaseExtension:
    def test_get_message_type(self):
        assert base_extension.get_message_type(base_extension.attributes) == "Approvals"

    # @patch("google.cloud.deploy_v1.services.cloud_deploy.CloudDeployClient")
    # def test_get_pipeline(self, mock_deploy_client):
    #     mock_pipeline = MagicMock(spec=DeliveryPipeline)
    #     mock_deploy_client.return_value.get_delivery_pipeline.return_value = (
    #         mock_pipeline
    #     )
    #     pipeline = base_extension.get_pipeline(
    #         "projects/project_id/locations/location_name/deliveryPipelines/pipeline_name"
    #     )
    #     assert pipeline == mock_pipeline

    @patch("google.cloud.deploy_v1.services.cloud_deploy.CloudDeployClient")
    def test_get_pipeline_with_permission_error(self, mock_deploy_client):
        mock_deploy_client.return_value.get_delivery_pipeline.side_effect = (
            PermissionDenied("Permission denied")
        )
        pipeline = base_extension.get_pipeline("pipeline_id")
        assert pipeline is None

    # @patch(
    #     "google.cloud.secretmanager_v1.services.secret_manager_service.SecretManagerServiceClient"
    # )
    # def test_get_config_from_secret(self, mock_secret_client):
    #     mock_secret_payload = Mock()
    #     mock_secret_payload.data.decode.return_value = json.dumps({"enabled": True})
    #     mock_secret_version_response = Mock(
    #         sm_types.AccessSecretVersionResponse(
    #             name="projects/project_id/secrets/mocked-secret",
    #             payload={},
    #         )
    #     )
    #     mock_secret_version_response.payload = mock_secret_payload
    #     mock_secret_client.return_value.access_secret_version.return_value = (
    #         mock_secret_version_response
    #     )
    #     secret_config = base_extension.get_config_from_secret(
    #         "projects/project_id/secrets/mocked-secret"
    #     )
    #     assert secret_config == {"enabled": True}

    @patch(
        "google.cloud.secretmanager_v1.services.secret_manager_service.SecretManagerServiceClient"
    )
    def test_get_config_from_secret_with_permission_error(self, mock_secret_client):
        mock_secret_client.return_value.access_secret_version.side_effect = (
            PermissionDenied("Permission denied")
        )
        secret_config = base_extension.get_config_from_secret(
            "projects/project_id/secrets/nonexistent-secret"
        )
        assert secret_config == {}

    @patch(
        "google.cloud.secretmanager_v1.services.secret_manager_service.SecretManagerServiceClient"
    )
    def test_get_config_from_secret_with_not_found_error(self, mock_secret_client):
        mock_secret_client.return_value.access_secret_version.side_effect = NotFound(
            "Secret not found"
        )
        secret_config = base_extension.get_config_from_secret(
            "projects/project_id/secrets/nonexistent-secret"
        )
        assert secret_config == {}
