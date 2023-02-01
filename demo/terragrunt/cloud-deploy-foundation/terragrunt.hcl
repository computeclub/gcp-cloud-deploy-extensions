include {
  path = find_in_parent_folders("terragrunt.hcl")
}

terraform {
  source = "github.com/computeclub/gcp-cloud-deploy-notifiers//terraform/cloud-deploy-notification-infra?ref=v0.1.0"
  # source = "${find_in_parent_folders("gcp-cloud-deploy-notifiers")}//terraform/cloud-deploy-notification-infra"
}

locals {
  config = read_terragrunt_config(find_in_parent_folders("config.hcl"))
}

inputs = {
  project_id = local.config.locals.project_id
}
