include {
  path = find_in_parent_folders("terragrunt.hcl")
}

terraform {
  source = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/artifact-registry?ref=v19.0.0"
}

locals {
  config = read_terragrunt_config(find_in_parent_folders("config.hcl.json"))
}

inputs = {
  description = "A docker registry repo for demo applications"
  id          = "demo"
  location    = "us"
  project_id  = local.config.locals.project_id
}
