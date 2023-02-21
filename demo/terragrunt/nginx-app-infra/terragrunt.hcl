include {
  path = find_in_parent_folders("terragrunt.hcl")
}

terraform {
  source = "${find_in_parent_folders("nginx-app")}//terraform"
  after_hook "after_hook" {
    commands = ["apply"]
    execute = [
      "gcloud",
      "builds",
      "submit",
      "--project=${local.config.locals.project_id}",
      "--substitutions=_EPOCH=${run_cmd("date", "+%s")},_REGISTRY_REPO_URL=${dependency.app_artifact_registry.outputs.artifact_registry_repo_endpoint}",
      "--config=${find_in_parent_folders("gcp-cloud-deploy-notifiers")}/demo/nginx-app/cloudbuild.yaml",
      "${find_in_parent_folders("gcp-cloud-deploy-notifiers")}/demo/nginx-app/"
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

dependency "release_auto_promoter_notifier" {
  config_path  = "${find_in_parent_folders("terragrunt")}/release-auto-promoter-notifier"
  mock_outputs = {}
}

dependency "image_tagger_notifier" {
  config_path  = "${find_in_parent_folders("terragrunt")}/image-tagger-notifier"
  mock_outputs = {}
}

inputs = {
  deployer_service_account_users = [
    "serviceAccount:${dependency.release_auto_promoter_notifier.outputs.workload_service_account.email}"
  ]
  enabled_cloud_deploy_notifiers = [
    dependency.echo_fastapi.outputs.config_annotation,
    dependency.release_auto_promoter_notifier.outputs.config_annotation,
    dependency.image_tagger_notifier.outputs.config_annotation,
  ]
  project_id = local.config.locals.project_id
}
