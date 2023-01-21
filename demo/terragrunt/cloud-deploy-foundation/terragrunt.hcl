include {
  path = find_in_parent_folders("terragrunt.hcl")
}

terraform {
  # TODO(brandonjbjelland): switch to a tag ref
  # source = "github.com/computeclub/gcp-cloud-deploy-notifiers//terraform/cloud-deploy-notification-infra?ref=main"
  source = "${find_in_parent_folders("gcp-cloud-deploy-notifiers")}//terraform/cloud-deploy-notification-infra"
}

locals {
  config = read_terragrunt_config(find_in_parent_folders("config.hcl"))
}

inputs = {
  project_id = local.config.locals.project_id
}
