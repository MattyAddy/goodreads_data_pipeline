variable "project" {
  description = "Project Title"
  default = "goodreads-madams"
}

variable "credentials" {
  type        = string
  default     = "/home/madams/.google/credentials/google_credentials.json"
  description = "GCP Credentials"
}

variable "location" {
  description = "Location"
  default = "US"
}

variable "region" {
  description = "Region"
  default = "us-east1"
}

variable "gcs_bucket" {
  description = "Goodreads Data Lake"
  default = "madams-terraform-book-data-lake"
}

variable "big_query_dataset_raw" {
  description = "Goodreads Dataset Raw"
  default = "goodreads_db_raw"
}

variable "big_query_dataset" {
  description = "Goodreads Dataset"
  default = "goodreads_db"
}
