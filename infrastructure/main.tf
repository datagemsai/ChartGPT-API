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

# Resources
module "chartgpt_api" {
  source          = "./api"
  project_id      = var.project_id
  region          = var.region
  docker_registry = var.docker_registry
  deployment      = var.deployment
  git_sha         = data.external.git.result.sha
  secrets         = local.secrets
  depends_on      = [google_project_service.run_api, module.secret-manager]
}

module "chartgpt_app" {
  source          = "./api"
  project_id      = var.project_id
  region          = var.region
  docker_registry = var.docker_registry
  deployment      = var.deployment
  git_sha         = data.external.git.result.sha
  secrets         = local.secrets
  depends_on      = [google_project_service.run_api, module.secret-manager]
}

module "caddy" {
  source          = "./caddy"
  project_id      = var.project_id
  region          = var.region
  base_domain     = var.base_domain
  docker_registry = var.docker_registry
  deployment      = var.deployment
  git_sha         = data.external.git.result.sha
  secrets         = local.secrets
  depends_on      = [google_project_service.run_api, module.secret-manager]
}
