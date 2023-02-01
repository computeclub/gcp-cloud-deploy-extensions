variable "annotations" {
  default     = {}
  description = "the annotations to attach to the pipeline. These can be used to enable Cloud Deploy notifiers in a more manual way."
  type        = map(string)
}

variable "app_name" {
  default     = "nginx-app"
  description = "The name of the app being deployed"
  type        = string
}

variable "deployer_service_account_users" {
  default     = []
  description = "A list of fully qualified IAM members given serviceAccountUser access to the deployer SA. e.g. [ \"serviceAccount:my-notifier-sa@project-id.gserviceaccount.iam.com\"]"
  type        = list(string)
}

variable "enabled_cloud_deploy_notifiers" {
  default     = []
  description = "Fully qualified Cloud Deploy notifiers to enable on the app's deployment pipeline. This varible is the interface for creating annotations, secrets, and secret permissions necessary for Cloud Deploy notifiers. List entries should be in the form 'subdomain.domain.tld/notifier' matching that of the Cloud Deployer. e.g. [\"deploy-notifiers.computeclub.io/echo-fastapi\",]"
  type        = list(string)
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
