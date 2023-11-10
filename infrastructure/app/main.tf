variable "project_id" {}
variable "region" {}
variable "docker_registry" {}
variable "base_domain" {}
variable "docker_image" {}
variable "secrets" {
  type = map(string)
}
variable "service_account_email" {}

resource "google_cloud_run_v2_service" "chartgpt_app_service" {
  project  = var.project_id
  name     = "chartgpt-app"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      max_instance_count = 5
    }

    containers {
      image = var.docker_image

      resources {
        limits = {
          cpu    = "1"
          memory = "2048Mi"
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
    service_account = var.service_account_email
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

resource "google_cloud_run_domain_mapping" "chartgpt_app_service" {
  project  = var.project_id
  location = var.region
  name     = "streamlit.${var.base_domain}"

  metadata {
    namespace = var.project_id
  }

  spec {
    route_name = google_cloud_run_v2_service.chartgpt_app_service.name
  }
}

resource "google_cloud_run_service_iam_member" "run_all_users_chartgpt_app" {
  project  = var.project_id
  service  = google_cloud_run_v2_service.chartgpt_app_service.name
  location = google_cloud_run_v2_service.chartgpt_app_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
