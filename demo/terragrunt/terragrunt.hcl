terragrunt_version_constraint = ">= 0.42"

remote_state {
  backend = "gcs"
  config = {
    project              = local.config.locals.project_id
    prefix               = path_relative_to_include()
    bucket               = local.config.locals.remote_state_bucket
    location             = "us"
    gcs_bucket_labels    = {}
    skip_bucket_creation = false
  }
}

locals {
    config = read_terragrunt_config("${find_in_parent_folders("terragrunt")}/config.hcl")
}

generate "backend" {
  path      = "backend.tf"
  if_exists = "skip"
  contents  = <<EOF
terraform {
  backend "gcs" {}
  required_version = ">= 1.3.6"
}
EOF
}
