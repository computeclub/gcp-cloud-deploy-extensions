locals {
  app_deployer_project_roles = [
    "roles/clouddeploy.releaser",
    "roles/logging.logWriter",
    "roles/run.admin",
    # storage.buckets.create needed to create buckets that store logs and build artifacts
    "roles/storage.admin",
  ]
}

resource "google_service_account" "app" {
  for_each     = toset(keys(local.main_deployment_targets))
  project      = var.project_id
  account_id   = "${each.key}-${var.app_name}"
  display_name = "A terraform-managed service account for running the ${each.key} ${var.app_name} workload"
}

resource "google_service_account" "app_deployer" {
  project      = var.project_id
  account_id   = "${var.app_name}-deployer"
  display_name = "A terraform-managed service account for deploying ${var.app_name} workloads"
}

resource "google_service_account_iam_member" "app_deployer_is_user_of_app_sa" {
  for_each           = toset(keys(local.main_deployment_targets))
  service_account_id = google_service_account.app[each.key].name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.app_deployer.email}"
}

resource "google_project_iam_member" "app_deployer" {
  for_each = toset(local.app_deployer_project_roles)
  project  = var.project_id
  role     = each.key
  member   = "serviceAccount:${google_service_account.app_deployer.email}"
}

resource "google_secret_manager_secret_iam_member" "cloud_deploy_extensions_secret_accessor" {
  for_each  = google_secret_manager_secret.main
  project   = each.value.project
  secret_id = each.value.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${each.value.labels.extension}@${var.project_id}.iam.gserviceaccount.com"
}

resource "google_secret_manager_secret_iam_member" "cloud_deploy_extensions_secret_viewer" {
  for_each  = google_secret_manager_secret.main
  project   = each.value.project
  secret_id = each.value.secret_id
  role      = "roles/secretmanager.viewer"
  member    = "serviceAccount:${each.value.labels.extension}@${var.project_id}.iam.gserviceaccount.com"
}

resource "google_service_account_iam_member" "deployer_sa_users" {
  for_each           = toset(var.deployer_service_account_users)
  service_account_id = google_service_account.app_deployer.name
  role               = "roles/iam.serviceAccountUser"
  member             = each.key
}
