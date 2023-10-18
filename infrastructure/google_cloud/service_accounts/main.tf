variable "project_id" {}

resource "google_service_account" "chartgpt_api" {
  account_id   = "chartgpt-api"
  display_name = "ChartGPT API Service Account"
  description  = ""
}

resource "google_project_iam_member" "artifact_registry_admin" {
  project = var.project_id
  role    = "roles/artifactregistry.admin"
  member  = "serviceAccount:${google_service_account.chartgpt_api.email}"
}

resource "google_project_iam_member" "bigquery_data_viewer" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.chartgpt_api.email}"
}

resource "google_project_iam_member" "bigquery_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.chartgpt_api.email}"
}

resource "google_project_iam_member" "bigquery_read_session_user" {
  project = var.project_id
  role    = "roles/bigquery.readSessionUser"
  member  = "serviceAccount:${google_service_account.chartgpt_api.email}"
}

resource "google_project_iam_member" "cloud_datastore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.chartgpt_api.email}"
}

resource "google_project_iam_member" "firebase_admin_sdk_admin" {
  project = var.project_id
  role    = "roles/firebase.sdkAdminServiceAgent"
  member  = "serviceAccount:${google_service_account.chartgpt_api.email}"
}

resource "google_project_iam_member" "secret_manager_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.chartgpt_api.email}"
}
