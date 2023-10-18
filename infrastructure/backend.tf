terraform {
  backend "gcs" {
    bucket  = "7653f6e8da5c4073-bucket-tfstate"
    prefix  = "terraform/state"
  }
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.0.2"
    }
  }
}

provider "google" {
  project = var.project_id
}

# Create new multi-region storage bucket in the US
# with versioning enabled

# [START storage_kms_encryption_tfstate]
resource "google_kms_key_ring" "terraform_state" {
  name     = "${random_id.bucket_prefix.hex}-bucket-tfstate"
  location = var.region
}

resource "google_kms_crypto_key" "terraform_state_bucket" {
  name            = "test-terraform-state-bucket"
  key_ring        = google_kms_key_ring.terraform_state.id
  rotation_period = "86400s"

  lifecycle {
    prevent_destroy = false
  }
}

# Enable the Cloud Storage service account to encrypt/decrypt Cloud KMS keys
data "google_project" "project" {
}

resource "google_project_iam_member" "default" {
  project = data.google_project.project.project_id
  role    = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member  = "serviceAccount:service-${data.google_project.project.number}@gs-project-accounts.iam.gserviceaccount.com"
}
# [END storage_kms_encryption_tfstate]

# [START storage_bucket_tf_with_versioning]
resource "random_id" "bucket_prefix" {
  byte_length = 8
}

resource "google_storage_bucket" "default" {
  name          = "${random_id.bucket_prefix.hex}-bucket-tfstate"
  force_destroy = false
  location      = var.region
  storage_class = "STANDARD"
  versioning {
    enabled = true
  }
  encryption {
    default_kms_key_name = google_kms_crypto_key.terraform_state_bucket.id
  }
  depends_on = [
    google_project_iam_member.default
  ]
}
# [END storage_bucket_tf_with_versioning]
# [END storage_flask_google_cloud_quickstart_parent_tag]
