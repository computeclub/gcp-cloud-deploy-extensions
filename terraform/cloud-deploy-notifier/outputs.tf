output "config_annotation" {
  description = "The config annotation clients need attached to deployment pipelines to enable this notifier."
  value       = local.config_annotation
}

output "workload_service_account" {
  description = "All outputs of the terraform-managed Cloud Deploy notifier workload service account."
  value       = google_service_account.main
}
