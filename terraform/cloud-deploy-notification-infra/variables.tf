variable "project_id" {
  type        = string
  description = "The project_id where the artifact registry, pubsub topics, and Cloud Deploy pipelines live"
}

variable "location" {
  type        = string
  description = "The location of the artifact registry repo."
  default     = "us"
}

variable "repository_id" {
  type        = string
  description = "The name of the artifact registry repo that hosts notifier images."
  default     = "cloud-deploy-notifiers"
}

variable "disable_apis_on_destroy" {
  type        = bool
  description = "A boolean controlling how destroy behaves against service APIs."
  default     = false
}
