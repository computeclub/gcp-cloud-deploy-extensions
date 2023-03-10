variable "annotation_domain" {
  default     = "deploy-extensions.computeclub.io"
  description = "The extension's annotation domain prefix."
  type        = string
}

variable "artifact_registry_repo" {
  description = "A object having attribute outputs of the artifact registry repo hosting the extension image."
  type = object({
    format   = string
    location = string
    name     = string
    project  = string
  })
}

variable "extension_name" {
  description = "The name of the extension deployed by this module."
  type        = string
}

variable "cloud_deploy_extension_subscriptions" {
  default = [
    { topic = "clouddeploy-resources" },
    { topic = "clouddeploy-operations" },
    { topic = "clouddeploy-approvals" },
  ]
  description = "The pubsub topics for which this module should create subscriptions. Subscriptions can optionally have filters."
  type = list(object({
    filter = optional(string)
    topic  = string
  }))
}

variable "env_vars" {
  default     = []
  description = "a list of objects containing names and values of environment variables to attach to the cloud run workload."
  type = list(object({
    name  = string,
    value = string,
  }))
}

variable "project_id" {
  description = "The project_id where all resources are deployed."
  type        = string
}

variable "region" {
  description = ""
  type        = string
}

variable "workload_sa_project_roles" {
  type = list(string)
  default = [
    "roles/clouddeploy.viewer",
  ]
}
