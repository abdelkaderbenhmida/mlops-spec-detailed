terraform {
  required_version = ">= 1.3"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0, < 7.0"
    }
  }

  # GCS state backend. Bucket is supplied at init time:
  #   terraform init -backend-config="bucket=<your-state-bucket>"
  # or uncomment below and set state_bucket in terraform.tfvars.
  backend "gcs" {
    prefix = "mlops-platform/terraform/state"
  }
}
