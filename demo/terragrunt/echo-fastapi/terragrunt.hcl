include {
  path = find_in_parent_folders("terragrunt.hcl")
}

terraform {
  # TODO(brandonjbjelland): switch to a tag ref
  # source = "github.com/computeclub/gcp-cloud-deploy-notifiers//notifiers/echo-fastapi/terraform?ref=main"
  source = "${find_in_parent_folders("gcp-cloud-deploy-notifiers")}/notifiers/echo-fastapi//terraform"
  before_hook "before_hook" {
    commands = ["apply"]
    execute = [
      "gcloud",
      "builds",
      "submit",
      "--config=${find_in_parent_folders("gcp-cloud-deploy-notifiers")}/notifiers/echo-fastapi/cloudbuild.yaml",
      "--project=${local.config.locals.project_id}",
      "--substitutions=_REGISTRY_REPO_URL=${dependency.cloud_deploy_foundation.outputs.artifact_registry_repo_endpoint}",
      "${find_in_parent_folders("gcp-cloud-deploy-notifiers")}/notifiers/echo-fastapi/"
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
    artifact_registry_repo_endpoint = "us-docker.pkg.dev/project-id/cloud-deploy-notifiers"
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
