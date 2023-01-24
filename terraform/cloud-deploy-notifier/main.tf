locals {
  artifact_registry_repo_endpoint = format(
    "%s-%s.pkg.dev/%s/%s",
    var.artifact_registry_repo.location,
    lower(var.artifact_registry_repo.format),
    var.artifact_registry_repo.project,
    var.artifact_registry_repo.name,
  )
  config_annotation = "${var.annotation_domain}/${var.notifier_name}"
  env_vars = setunion(
    toset(var.env_vars),
    toset([{
      name  = "NOTIFIER_CONFIG_PIPELINE_ANNOTATION"
      value = local.config_annotation
    }])
  )
}

resource "google_pubsub_subscription" "main" {
  for_each             = { for entry in var.cloud_deploy_notification_subscriptions : entry.topic => entry }
  project              = var.project_id
  name                 = "${var.notifier_name}-${each.value.topic}-push"
  topic                = each.value.topic
  filter               = each.value.filter
  ack_deadline_seconds = 30
  labels = {
    repo_url      = "github0com_computeclub_gcp-cloud-deploy-notifiers"
    notifier_name = var.notifier_name
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
  name     = var.notifier_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  binary_authorization {
    use_default = true
  }
  template {
    service_account = google_service_account.main.email
    containers {
      image = "${local.artifact_registry_repo_endpoint}/${var.notifier_name}:latest"
      dynamic "env" {
        for_each = local.env_vars
        content {
          name  = env.value["name"]
          value = env.value["value"]
        }
      }
    }
  }

  labels = {
    repo_url      = "github0com_computeclub_gcp-cloud-deploy-notifiers"
    notifier_name = var.notifier_name
  }
}
