variable "deployment" {
  type    = string
  default = "staging"
}

variable "base_domain" {
  type    = string
  default = "chartgpt-staging.cadlabs.org"
}

variable "project_id" {
  type    = string
  default = "chartgpt-staging"
}

variable "region" {
  type    = string
  default = "europe-west4"
}

variable "docker_registry" {
  type    = string
  default = "europe-west3-docker.pkg.dev"
}

locals {
  secrets = lookup(yamldecode(file("../app_secrets_${var.deployment}.yaml")), "env_variables", {})
}

resource "google_project_service" "run_api" {
  project            = var.project_id
  service            = "run.googleapis.com"
  disable_on_destroy = true
}

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
      image = "${var.docker_registry}/${var.project_id}/${var.project_id}/chartgpt-app"

      resources {
        limits = {
          cpu    = "1"
          memory = "2048Mi"
        }
      }

      dynamic "env" {
        for_each = local.secrets
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

  # Waits for the Cloud Run API to be enabled
  depends_on = [google_project_service.run_api, module.secret-manager]
}

resource "google_cloud_run_domain_mapping" "chartgpt_app_service" {
  project  = var.project_id
  location = var.region
  name     = "chartgpt-app-${var.deployment}.cadlabs.org"

  metadata {
    namespace = var.project_id
  }

  spec {
    route_name = google_cloud_run_v2_service.chartgpt_app_service.name
  }
}

resource "google_cloud_run_v2_service" "caddy_service" {
  project  = var.project_id
  name     = "caddy"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      max_instance_count = 2
    }

    containers {
      image = "${var.docker_registry}/${var.project_id}/${var.project_id}/caddy"
      volume_mounts {
        name       = "caddy_data"
        mount_path = "/data"
      }
      volume_mounts {
        name       = "caddy_config"
        mount_path = "/config"
      }
      env {
        name  = "version"
        value = local.secrets.VERSION
      }
      env {
        name  = "deployment"
        value = var.deployment
      }
      env {
        name  = "base_domain"
        value = var.base_domain
      }
      env {
        name  = "cloudflare_api_token"
        value = local.secrets.CLOUDFLARE_API_TOKEN
      }
    }
    volumes {
      name = "caddy_data"
    }
    volumes {
      name = "caddy_config"
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  # Waits for the Cloud Run API to be enabled
  depends_on = [google_project_service.run_api, module.secret-manager]
}

resource "google_cloud_run_domain_mapping" "caddy_service" {
  project  = var.project_id
  location = var.region
  name     = var.base_domain

  metadata {
    namespace = var.project_id
  }

  spec {
    route_name = google_cloud_run_v2_service.caddy_service.name
  }
}

resource "google_cloud_run_domain_mapping" "caddy_service_www" {
  project  = var.project_id
  location = var.region
  name     = "www.${var.base_domain}"

  metadata {
    namespace = var.project_id
  }

  spec {
    route_name = google_cloud_run_v2_service.caddy_service.name
  }
}

resource "google_cloud_run_domain_mapping" "caddy_service_app" {
  project  = var.project_id
  location = var.region
  name     = "app.${var.base_domain}"

  metadata {
    namespace = var.project_id
  }

  spec {
    route_name = google_cloud_run_v2_service.caddy_service.name
  }
}

# Allow unauthenticated users to invoke the service
resource "google_cloud_run_service_iam_member" "run_all_users_chartgpt_app" {
  project  = var.project_id
  service  = google_cloud_run_v2_service.chartgpt_app_service.name
  location = google_cloud_run_v2_service.chartgpt_app_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "run_all_users_caddy" {
  project  = var.project_id
  service  = google_cloud_run_v2_service.caddy_service.name
  location = google_cloud_run_v2_service.caddy_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Create secrets in Google Secret Manager
module "secret-manager" {
  source     = "GoogleCloudPlatform/secret-manager/google"
  version    = "~> 0.1"
  project_id = var.project_id
  secrets = [
    for name, secret in local.secrets :
    {
      name                  = name
      automatic_replication = true
      secret_data           = secret
    }
  ]
}
