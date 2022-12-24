include {
  path = find_in_parent_folders("terragrunt.hcl")
}

terraform {
  # TODO(brandonjbjelland): switch to a tag ref
  # source = "github.com/computeclub/gcp-cloud-deploy-reactors//demo/nginx-app/terraform?ref=main"
  source = "${find_in_parent_folders("nginx-app")}//terraform"
  after_hook "after_hook" {
    commands = ["apply"]
    execute = [
      "gcloud",
      "builds",
      "submit",
      "--project=${local.config.locals.project_id}",
      "--substitutions=_EPOCH=${run_cmd("date", "+%s")},_REGISTRY_REPO_URL=${dependency.app_artifact_registry.outputs.artifact_registry_repo_endpoint}",
      "--config=${find_in_parent_folders("gcp-cloud-deploy-reactors")}/demo/nginx-app/cloudbuild.yaml",
      "${find_in_parent_folders("gcp-cloud-deploy-reactors")}/demo/nginx-app/"
    ]
  }
}

locals {
  config = read_terragrunt_config(find_in_parent_folders("config.hcl"))
}

dependency "app_artifact_registry" {
  config_path  = "${find_in_parent_folders("terragrunt")}/app-artifact-registry"
  mock_outputs = {}
}

dependency "echo_fastapi" {
  config_path  = "${find_in_parent_folders("terragrunt")}/echo-fastapi"
  mock_outputs = {}
}


inputs = {
  enabled_cloud_deployers = [
    dependency.echo_fastapi.outputs.config_annotation,
  ]
  project_id = local.config.locals.project_id
}