include {
  path = find_in_parent_folders("terragrunt.hcl")
}

terraform {
  source = "github.com/computeclub/gcp-cloud-deploy-extensions//terraform/cloud-deploy-extension?ref=v0.1.1"
  # source = "${find_in_parent_folders("gcp-cloud-deploy-extensions")}//terraform/cloud-deploy-extension"
  before_hook "before_hook" {
    commands = ["apply"]
    execute = [
      "gcloud",
      "builds",
      "submit",
      "--config=${local.extension_path}/cloudbuild.yaml",
      "--project=${local.config.locals.project_id}",
      "--substitutions=_REGISTRY_REPO_URL=${dependency.cloud_deploy_foundation.outputs.artifact_registry_repo_endpoint}",
      "${local.extension_path}/"
    ]
  }
}

locals {
  config         = read_terragrunt_config(find_in_parent_folders("config.hcl"))
  extension_path = "${find_in_parent_folders("gcp-cloud-deploy-extensions")}/extensions/echo-fastapi"
}

dependency "cloud_deploy_foundation" {
  config_path = "${find_in_parent_folders("terragrunt")}/cloud-deploy-foundation"
  mock_outputs = {
    artifact_registry_repo = {
      location = "foo"
      name     = "bar"
      format   = "docker"
      project  = "my-project-id"
    }
    cloud_deploy_pubsub_topics = {
      clouddeploy-resources  = {}
      clouddeploy-operations = {}
      clouddeploy-approvals  = {}
    }
  }
}

inputs = {
  artifact_registry_repo = dependency.cloud_deploy_foundation.outputs.artifact_registry_repo
  env_vars = [
    {
      name  = "LOG_LEVEL"
      value = "DEBUG"
    },
    {
      name = "SRC_SHA1"
      value = sha1(
        join(
          "",
          [
            for f in fileset(
              "${local.extension_path}/",
              "**"
            ) : filesha1("${local.extension_path}/${f}")
          ]
        )
      )
    },
  ]
  extension_name = "echo-fastapi"
  project_id     = local.config.locals.project_id
  region         = "us-central1"
}
