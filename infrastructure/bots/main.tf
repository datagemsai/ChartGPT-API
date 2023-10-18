# This code is compatible with Terraform 4.25.0 and versions that are backwards compatible to 4.25.0.
# For information about validating this Terraform code, see https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/google-cloud-platform-build#format-and-validate-the-configuration

variable "project_id" {}
variable "region" {}
variable "docker_registry" {}
variable "deployment" {}
variable "slack_docker_image" {}
variable "telegram_docker_image" {}
variable "discord_docker_image" {}
variable "secrets" {
  type = map(string)
}
variable "service_account_email" {}

locals {
  export_secrets = join("\n", [
    for secret in keys(var.secrets) :
    "export TF_${secret}=$(gcloud secrets versions access latest --secret=\"${secret}\")"
  ])

  docker_env_vars = join(" ", [
    for secret in keys(var.secrets) :
    "-e ${secret}=$TF_${secret}"
  ])
}

resource "google_compute_instance" "chartgpt-bots" {
  name = "chartgpt-bots"
  project = var.project_id
  zone = "${var.region}-a"
  machine_type = "e2-medium"

  boot_disk {
    auto_delete = true
    device_name = "chartgpt-bots"

    initialize_params {
      image = "projects/debian-cloud/global/images/debian-11-bullseye-v20230912"
      size  = 10
      type  = "pd-balanced"
    }

    mode = "READ_WRITE"
  }

  can_ip_forward      = false
  deletion_protection = false
  enable_display      = false
  allow_stopping_for_update = true

  labels = {
    goog-ec-src = "vm_add-tf"
  }

  network_interface {
    access_config {
      network_tier = "PREMIUM"
    }

    subnetwork = "projects/${var.project_id}/regions/${var.region}/subnetworks/default"
  }

  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
    preemptible         = false
    provisioning_model  = "STANDARD"
  }

  service_account {
    email  = var.service_account_email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  shielded_instance_config {
    enable_integrity_monitoring = true
    enable_secure_boot          = false
    enable_vtpm                 = true
  }

  metadata_startup_script = <<-EOT
    #!/bin/bash
    apt-get update
    apt-get install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
    apt-get update
    apt-get install -y docker-ce

    # Docker client must be configured to authenticate
    gcloud auth configure-docker ${var.docker_registry}

    # Fetch secrets from Secret Manager
    ${local.export_secrets}

    # Run Docker containers
    docker run -d ${local.docker_env_vars} ${var.slack_docker_image}
    docker run -d ${local.docker_env_vars} ${var.telegram_docker_image}
    docker run -d ${local.docker_env_vars} ${var.discord_docker_image}
  EOT
}
