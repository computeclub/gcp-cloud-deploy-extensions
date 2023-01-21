
output "secrets" {
  description = "The secrets that cloud_deploy_notifiers use to read config and operate against this application deployment pipeline"
  value       = google_secret_manager_secret.main
}
