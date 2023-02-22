resource "google_service_account" "main" {
  project      = var.project_id
  account_id   = var.extension_name
  display_name = "A terraform-managed Cloud Deploy extension workload service account"
}

resource "google_project_iam_member" "main" {
  for_each = toset(var.workload_sa_project_roles)
  project  = var.project_id
  role     = each.key
  member   = "serviceAccount:${google_service_account.main.email}"
}

resource "google_artifact_registry_repository_iam_member" "main" {
  project    = var.project_id
  location   = var.artifact_registry_repo.location
  repository = var.artifact_registry_repo.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.main.email}"
}

resource "google_service_account" "invoker" {
  project      = var.project_id
  account_id   = "${var.extension_name}-invoker"
  display_name = "A terraform-managed Cloud Deploy extension pubsub invoker service account"
}

# from: https://cloud.google.com/run/docs/tutorials/pubsub#integrating-pubsub
resource "google_cloud_run_service_iam_member" "invoker" {
  location = google_cloud_run_v2_service.main.location
  project  = google_cloud_run_v2_service.main.project
  service  = google_cloud_run_v2_service.main.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.invoker.email}"
}
