output "cloud_deploy_pubsub_topics" {
  value = google_pubsub_topic.main
}

output "artifact_registry_repo" {
  value = google_artifact_registry_repository.main
}

output "artifact_registry_repo_endpoint" {
  description = "A conventional endpoint for this repo: https://cloud.google.com/artifact-registry/docs/docker/pushing-and-pulling"
  value       = format("%s-%s.pkg.dev/%s/%s", google_artifact_registry_repository.main.location, lower(google_artifact_registry_repository.main.format), var.project_id, google_artifact_registry_repository.main.name)
}
