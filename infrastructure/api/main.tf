variable "project_id" {}
variable "region" {}
variable "docker_registry" {}
variable "deployment" {}
variable "docker_image" {}
variable "secrets" {
  type = map(string)
}

resource "google_cloud_run_v2_service" "chartgpt_api_service" {
  project  = var.project_id
  name     = "chartgpt-api"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    timeout = "900s"

    scaling {
      min_instance_count = 1
      max_instance_count = 5
    }

    containers {
      image = var.docker_image

      resources {
        cpu_idle = true
        limits = {
          cpu    = "4"
          memory = "4096Mi"
        }
      }

      dynamic "env" {
        for_each = var.secrets
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = env.key
              version = "latest"
            }
          }
        }
      }
    }
    service_account = "chartgpt-app-${var.deployment}@${var.project_id}.iam.gserviceaccount.com"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

resource "google_cloud_run_domain_mapping" "chartgpt_api_service" {
  project  = var.project_id
  location = var.region
  name     = "chartgpt-api-${var.deployment}.***REMOVED***"

  metadata {
    namespace = var.project_id
  }

  spec {
    route_name = google_cloud_run_v2_service.chartgpt_api_service.name
  }
}

resource "google_cloud_run_service_iam_member" "run_all_users_chartgpt_api" {
  project  = var.project_id
  service  = google_cloud_run_v2_service.chartgpt_api_service.name
  location = google_cloud_run_v2_service.chartgpt_api_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
