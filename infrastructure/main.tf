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
  secrets                   = lookup(yamldecode(file("../app_secrets_${var.deployment}.yaml")), "env_variables", {})
  chartgpt_api_image_latest = "${var.docker_registry}/${var.project_id}/${var.project_id}/chartgpt-api@${data.docker_registry_image.chartgpt_api_image.sha256_digest}"
  chartgpt_app_image_latest = "${var.docker_registry}/${var.project_id}/${var.project_id}/chartgpt-app@${data.docker_registry_image.chartgpt_app_image.sha256_digest}"
  caddy_image_latest        = "${var.docker_registry}/${var.project_id}/${var.project_id}/caddy@${data.docker_registry_image.caddy_image.sha256_digest}"
}

resource "google_project_service" "run_api" {
  project            = var.project_id
  service            = "run.googleapis.com"
  disable_on_destroy = true
}

data "external" "git" {
  program = [
    "git",
    "log",
    "--pretty=format:{ \"sha\": \"%h\" }",
    "-1",
    "HEAD"
  ]
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

// See
// https://github.com/terraform-providers/terraform-provider-google/issues/6706#issuecomment-652009984
// https://github.com/terraform-providers/terraform-provider-google/issues/6635#issuecomment-647858867

data "google_client_config" "default" {}

terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.0.2"
    }
  }
}

provider "docker" {
  registry_auth {
    address  = "europe-west3-docker.pkg.dev"
    username = "oauth2accesstoken"
    password = data.google_client_config.default.access_token
  }
}

# ChartGPT API Docker image
data "docker_registry_image" "chartgpt_api_image" {
  name = "${var.docker_registry}/${var.project_id}/${var.project_id}/chartgpt-api"
}

# ChartGPT App Docker image
data "docker_registry_image" "chartgpt_app_image" {
  name = "${var.docker_registry}/${var.project_id}/${var.project_id}/chartgpt-app"
}

# Caddy Docker image
data "docker_registry_image" "caddy_image" {
  name = "${var.docker_registry}/${var.project_id}/${var.project_id}/caddy"
}

# Resources
module "chartgpt_api" {
  source          = "./api"
  project_id      = var.project_id
  region          = var.region
  docker_registry = var.docker_registry
  deployment      = var.deployment
  secrets         = local.secrets
  docker_image    = local.chartgpt_api_image_latest
  depends_on      = [google_project_service.run_api, module.secret-manager]
}

module "chartgpt_app" {
  source          = "./app"
  project_id      = var.project_id
  region          = var.region
  docker_registry = var.docker_registry
  deployment      = var.deployment
  secrets         = local.secrets
  docker_image    = local.chartgpt_app_image_latest
  depends_on      = [google_project_service.run_api, module.secret-manager]
}

module "caddy" {
  source          = "./caddy"
  project_id      = var.project_id
  region          = var.region
  base_domain     = var.base_domain
  docker_registry = var.docker_registry
  deployment      = var.deployment
  secrets         = local.secrets
  docker_image    = local.caddy_image_latest
  depends_on      = [google_project_service.run_api, module.secret-manager]
}
