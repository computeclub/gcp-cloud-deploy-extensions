include {
  path = find_in_parent_folders("terragrunt.hcl")
}

terraform {
  # TODO(brandonjbjelland): switch to a tag ref
  # source = "github.com/computeclub/gcp-cloud-deploy-reactors//reactors/echo-fastapi/terraform?ref=main"
  source = "${find_in_parent_folders("gcp-cloud-deploy-reactors")}/reactors/echo-fastapi//terraform"
  before_hook "before_hook" {
    commands = ["apply"]
    execute = [
      "gcloud",
      "builds",
      "submit",
      "--project=${local.config.locals.project_id}",
      "--tag=${dependency.cloud_deploy_foundation.outputs.artifact_registry_repo_endpoint}/echo-fastapi:latest",
      "${find_in_parent_folders("gcp-cloud-deploy-reactors")}/reactors/echo-fastapi/"
    ]
  }
}

locals {
  config = read_terragrunt_config(find_in_parent_folders("config.hcl"))
}

dependency "cloud_deploy_foundation" {
  config_path = "${find_in_parent_folders("terragrunt")}/cloud-deploy-foundation"
  mock_outputs = {
    artifact_registry_repo = {
      location = "foo"
      name     = "bar"
    }
    artifact_registry_repo_endpoint = "us-docker.pkg.dev/project-id/cloud-deploy-reactors"
    cloud_deploy_pubsub_topics = {
      clouddeploy-resources  = {}
      clouddeploy-operations = {}
      clouddeploy-approvals  = {}
    }
  }
}

inputs = {
  artifact_registry_repo          = dependency.cloud_deploy_foundation.outputs.artifact_registry_repo
  artifact_registry_repo_endpoint = dependency.cloud_deploy_foundation.outputs.artifact_registry_repo_endpoint
  project_id                      = local.config.locals.project_id
  region                          = "us-central1"
}
