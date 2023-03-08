terragrunt_version_constraint = ">= 0.42"

terraform {
  after_hook "set_success" {
    commands     = ["apply"]
    execute      = ["touch", "${get_terragrunt_dir()}/.tg_state"]
    run_on_error = false
  }
  error_hook "set_failure" {
    commands = ["apply"]
    execute  = ["rm", "${get_terragrunt_dir()}/.tg_state"]
    on_errors = [
      ".*",
    ]
  }
}

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
  config = read_terragrunt_config("${find_in_parent_folders("terragrunt")}/config.hcl.json")
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
