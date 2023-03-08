include {
  path = find_in_parent_folders("terragrunt.hcl")
}

terraform {
  source = "github.com/computeclub/gcp-cloud-deploy-extensions//terraform/cloud-deploy-extension-infra?ref=main"
  # source = "${find_in_parent_folders("gcp-cloud-deploy-extensions")}//terraform/cloud-deploy-extension-infra"
}

locals {
  config = read_terragrunt_config(find_in_parent_folders("config.hcl.json"))
}

inputs = {
  project_id = local.config.locals.project_id
}
