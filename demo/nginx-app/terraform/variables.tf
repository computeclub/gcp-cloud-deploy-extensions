variable "annotations" {
  default     = {}
  description = "the annotations to attach to the pipeline. These can be used to enable Cloud Deploy reactors in a more manual way."
  type        = map(string)
}

variable "enabled_cloud_deployers" {
  default     = []
  description = "Fully qualified deployers to enable on the app's deployment pipeline. This varible is the interface for creating annotations, secrets, and secret permissions necessary for deployers. List entries should be in the form 'subdomain.domain.tld/deployer' matching that of the Cloud Deployer. e.g. [\"deployers.computeclub.io/echo-fastapi\",]"
  type        = list(string)
}

variable "app_name" {
  default     = "nginx-app"
  description = "The name of the app being deployed"
  type        = string
}

variable "labels" {
  default     = {}
  description = "the labels to attach to the pipeline. These are purely metadata for humans"
  type        = map(string)
}

variable "project_id" {
  type        = string
  description = ""
}

variable "region" {
  default     = "us-central1"
  description = "The name of the app being deployed"
  type        = string
}