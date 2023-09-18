variable "project_id" {}
variable "region" {}
variable "base_domain" {}
variable "docker_registry" {}
variable "deployment" {}
variable "docker_image" {}
variable "secrets" {
  type = map(string)
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
      image = var.docker_image

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
        value = var.secrets.VERSION
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
        value = var.secrets.CLOUDFLARE_API_TOKEN
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

resource "google_cloud_run_domain_mapping" "caddy_service_api" {
  project  = var.project_id
  location = var.region
  name     = "api.${var.base_domain}"

  metadata {
    namespace = var.project_id
  }

  spec {
    route_name = google_cloud_run_v2_service.caddy_service.name
  }
}

resource "google_cloud_run_service_iam_member" "run_all_users_caddy" {
  project  = var.project_id
  service  = google_cloud_run_v2_service.caddy_service.name
  location = google_cloud_run_v2_service.caddy_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
