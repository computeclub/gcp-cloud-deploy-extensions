# TODO(brandonjacob): the core of this will be pulled into a module that other
# notifiers can share as a foundation. Bits like IAM can differ potentially enough
# to warrant separation between notifier-core-infra and notifier-specific resources
locals {
  artifact_registry_repo_endpoint = var.artifact_registry_repo_endpoint == "" ? "us-docker.pkg.dev/${var.project_id}/cloud-deploy-notifiers" : var.artifact_registry_repo_endpoint
  cloud_deploy_notification_topics = [
    "clouddeploy-resources",
    "clouddeploy-operations",
    "clouddeploy-approvals",
  ]
  config_annotation = "deploy-notifiers.computeclub.io/${var.deployer_name}"
}

# TODO(brandonjbjelland): demonstrate a filter

resource "google_pubsub_subscription" "main" {
  for_each             = toset(local.cloud_deploy_notification_topics)
  project              = var.project_id
  name                 = "${var.deployer_name}-${each.key}-push"
  topic                = each.key
  ack_deadline_seconds = 30
  labels = {
    repo_url      = "github0com_computeclub_gcp-cloud-deploy-notifiers"
    deployer_name = var.deployer_name
  }
  push_config {
    push_endpoint = "${google_cloud_run_v2_service.main.uri}/"
    oidc_token {
      audience              = google_cloud_run_v2_service.main.uri
      service_account_email = google_service_account.invoker.email
    }
  }
}

# TODO(brandonjbjelland): add a deadletter topic and pull sub


resource "google_cloud_run_v2_service" "main" {
  project  = var.project_id
  name     = var.deployer_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  binary_authorization {
    use_default = true
  }
  template {
    service_account = google_service_account.main.email
    containers {
      image = "${local.artifact_registry_repo_endpoint}/${var.deployer_name}:latest"
      env {
        # if this annotation is present on a Cloud Deploy pipeline, this notifier
        # will be considered active on that pipeline. In scenarios requiring
        # configuration, the value should point to a fully-qualified secret
        name  = "DEPLOYER_CONFIG_PIPELINE_ANNOTATION"
        value = local.config_annotation
      }
      env {
        # TODO(brandonjbjelland): migrate away from latest tags and remove this env var that forces redeploy
        # alternatively: use the md5sum of the src dir
        name  = "DEPLOY_TIMESTAMP"
        value = timestamp()
      }
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
    }
  }

  labels = {
    repo_url      = "github0com_computeclub_gcp-cloud-deploy-notifiers"
    deployer_name = var.deployer_name
  }
}
