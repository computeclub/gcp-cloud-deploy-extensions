include {
  path = find_in_parent_folders("terragrunt.hcl")
}

terraform {
  # TODO(brandonjbjelland): switch to a tag ref
  # source = "github.com/computeclub/gcp-cloud-deploy-notifiers//terraform/cloud-deploy-notifier?ref=main"
  source = "${find_in_parent_folders("gcp-cloud-deploy-notifiers")}//terraform/cloud-deploy-notifier"
  before_hook "before_hook" {
    commands = ["apply"]
    execute = [
      "gcloud",
      "builds",
      "submit",
      "--config=${local.notifier_path}/cloudbuild.yaml",
      "--project=${local.config.locals.project_id}",
      "--substitutions=_REGISTRY_REPO_URL=${dependency.cloud_deploy_foundation.outputs.artifact_registry_repo_endpoint}",
      "${local.notifier_path}/"
    ]
  }
}

locals {
  config        = read_terragrunt_config(find_in_parent_folders("config.hcl"))
  notifier_path = "${find_in_parent_folders("gcp-cloud-deploy-notifiers")}/notifiers/echo-fastapi"
}

dependency "cloud_deploy_foundation" {
  config_path = "${find_in_parent_folders("terragrunt")}/cloud-deploy-foundation"
  mock_outputs = {
    artifact_registry_repo = {
      location = "foo"
      name     = "bar"
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
      value = "INFO"
    },
    {
      name  = "SRC_SHA1"
      value = sha1(join("", [for f in fileset("${local.notifier_path}/src", "*") : filesha1("${local.notifier_path}/src/${f}")]))
    },
  ]
  notifier_name = "echo-fastapi"
  project_id    = local.config.locals.project_id
  region        = "us-central1"
}
