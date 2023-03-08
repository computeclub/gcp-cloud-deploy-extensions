include {
  path = find_in_parent_folders("terragrunt.hcl")
}

terraform {
  # TODO(bjb): bump this to main before merge and all sources to v0.2.0 when released
  source = "${find_in_parent_folders("gcp-cloud-deploy-extensions")}//terraform/cloud-deploy-extension"
  # source = "github.com/computeclub/gcp-cloud-deploy-extensions//terraform/cloud-deploy-extension?ref=main"
  # source = "github.com/computeclub/gcp-cloud-deploy-extensions//terraform/cloud-deploy-extension?ref=v0.2.0"
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
  config         = read_terragrunt_config(find_in_parent_folders("config.hcl.json"))
  extension_path = "${find_in_parent_folders("gcp-cloud-deploy-extensions")}/extensions/image-tagger"
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
  cloud_deploy_extension_subscriptions = [
    {
      topic  = "clouddeploy-operations"
      filter = "attributes.Action = \"Succeed\" AND attributes.ResourceType = \"Rollout\""
    },
  ]
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
  extension_name = "image-tagger"
  project_id     = local.config.locals.project_id
  region         = "us-central1"
  workload_sa_project_roles = [
    "roles/artifactregistry.writer",
    "roles/clouddeploy.viewer",
    # TODO(bjb): revisit if gcr.io permissions are needed. these roles dont seem to exist
  ]
}
