output "config_annotation" {
  description = "The config annotation clients need attached to deployment pipelines to enable this extension."
  value       = local.config_annotation
}

output "workload_service_account" {
  description = "All outputs of the terraform-managed Cloud Deploy extension workload service account."
  value       = google_service_account.main
}
