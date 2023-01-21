variable "artifact_registry_repo" {
  description = ""
  type = object({
    location = string
    name     = string
  })
}

variable "artifact_registry_repo_endpoint" {
  description = ""
  default     = ""
  type        = string
}

variable "deployer_name" {
  default = "echo-fastapi"
  type    = string
}

variable "project_id" {
  description = ""
  type        = string
}

variable "region" {
  type        = string
  description = ""
}
