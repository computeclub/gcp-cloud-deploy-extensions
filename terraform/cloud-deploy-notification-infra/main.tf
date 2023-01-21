locals {
  cloud_deploy_notification_topics = [
    "clouddeploy-resources",
    "clouddeploy-operations",
    "clouddeploy-approvals",
  ]
  service_apis = [
    "binaryauthorization.googleapis.com",
    "cloudbuild.googleapis.com",
    "clouddeploy.googleapis.com",
    "pubsub.googleapis.com",
    "run.googleapis.com",
    "secretmanager.googleapis.com",
    "serviceusage.googleapis.com",
  ]
}

resource "google_project_service" "main" {
  for_each           = toset(local.service_apis)
  project            = var.project_id
  service            = each.key
  disable_on_destroy = var.disable_apis_on_destroy
}

resource "google_pubsub_topic" "main" {
  for_each = toset(local.cloud_deploy_notification_topics)
  project  = var.project_id
  name     = each.key
}

resource "google_artifact_registry_repository" "main" {
  project       = var.project_id
  location      = var.location
  repository_id = var.repository_id
  description   = "A docker registry repo for Cloud Deploy notifiers"
  format        = "DOCKER"
}

resource "google_project_service_identity" "pubsub" {
  provider = google-beta
  project  = var.project_id
  service  = "pubsub.googleapis.com"
}

# https://cloud.google.com/run/docs/tutorials/pubsub#integrating-pubsub
resource "google_project_iam_member" "legacy_pubsub_service_agent" {
  project = var.project_id
  role    = "roles/iam.serviceAccountTokenCreator"
  member  = "serviceAccount:${google_project_service_identity.pubsub.email}"
}
