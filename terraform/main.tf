terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "6.9.0"
    }
  }
}

provider "google" {
  credentials = file(var.credentials)
  project = var.project
  region  = var.region
}

resource "google_storage_bucket" "book_data_lake" {
  name          = var.gcs_bucket
  location      = var.location
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

resource "google_bigquery_dataset_raw" "goodreads_db_raw" {
  dataset_id = var.big_query_dataset_raw
  location   = var.location
}

resource "google_bigquery_dataset" "goodreads_db" {
  dataset_id = var.big_query_dataset
  location   = var.location
}
