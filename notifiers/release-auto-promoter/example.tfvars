# using ../../terraform/cloud-deploy-notifier

artifact_registry_repo = {
  format   = "docker"
  location = "us"
  name     = "my-registry-repo"
  project  = "my-project-id"
}
cloud_deploy_notification_subscriptions = [
  {
    topic = "clouddeploy-operations"
    # filters = ""
  },
]
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
notifier_name = "release-auto-promoter"
project_id    = "my-project-id"
region        = "us-central1"
workload_sa_project_roles = [
  "roles/clouddeploy.releaser",
]
