locals {
  main_deployment_targets = {
    "dev" = {
      require_approval = false
    }
    "staging" = {
      require_approval = false
    }
    "prod" = {
      require_approval = true
    }
  }

  cloud_deploy_extensions = { for ecd in var.enabled_cloud_deploy_extensions :
    ecd => google_secret_manager_secret.main[ecd].name
  }
  annotations = merge(
    var.annotations,
    local.cloud_deploy_extensions
  )
}

resource "google_clouddeploy_delivery_pipeline" "main" {
  provider    = google-beta
  location    = var.region
  name        = var.app_name
  description = "The deployment pipeline for all ${var.app_name} environments"
  annotations = local.annotations
  labels      = var.labels
  project     = var.project_id
  serial_pipeline {
    stages {
      profiles  = ["dev"]
      target_id = google_clouddeploy_target.main["dev"].name
      strategy {
        standard {
          verify = true
        }
      }
    }
    stages {
      profiles  = ["staging"]
      target_id = google_clouddeploy_target.main["staging"].name
      strategy {
        standard {
          verify = true
        }
      }
    }
    stages {
      profiles  = ["prod"]
      target_id = google_clouddeploy_target.main["prod"].name
      strategy {
        standard {
          verify = true
        }
      }
    }
  }
}

resource "google_clouddeploy_target" "main" {
  provider = google-beta
  for_each = local.main_deployment_targets
  location = var.region
  project  = var.project_id
  name     = "${var.app_name}-${each.key}"
  labels   = {}
  annotations = merge(
    local.annotations,
    {
      "ENVIRONMENT" = each.key
    }
  )
  description = "The ${var.app_name} ${each.key} deployment target"
  execution_configs {
    usages = [
      "RENDER",
      "DEPLOY",
      "VERIFY",
    ]
    execution_timeout = "900s"
    service_account   = google_service_account.app_deployer.email
  }
  require_approval = each.value.require_approval
  run {
    location = "projects/${var.project_id}/locations/${var.region}"
  }
}

resource "google_secret_manager_secret" "main" {
  for_each  = toset(var.enabled_cloud_deploy_extensions)
  project   = var.project_id
  secret_id = format("%s-%s", var.app_name, split("/", each.key)[1])
  labels = {
    app       = var.app_name
    extension = split("/", each.key)[1]
  }
  replication {
    automatic = true
  }
}
