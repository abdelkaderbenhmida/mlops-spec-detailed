variable "project_id" {
  description = "GCP project ID where the platform is deployed."
  type        = string
}

variable "region" {
  description = "GCP region for all resources."
  type        = string
  default     = "europe-west1"
}

variable "zone" {
  description = "GCP zone for all compute instances."
  type        = string
  default     = "europe-west1-b"
}

variable "admin_ip" {
  description = "Admin IP (CIDR) allowed SSH access via sg-mgmt. e.g. 203.0.113.10/32"
  type        = string
}

variable "ssh_public_key" {
  description = "Path to the SSH public key file injected into every VM."
  type        = string
}

variable "state_bucket" {
  description = "GCS bucket for Terraform remote state (used via -backend-config)."
  type        = string
  default     = ""
}

variable "vpc_name" {
  description = "Name of the VPC."
  type        = string
  default     = "mlops-vpc"
}

variable "vpc_cidr" {
  description = "VPC CIDR block (spec section 2)."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "Public subnet: ingress/LB entrypoint only."
  type        = string
  default     = "10.0.1.0/24"
}

variable "public_subnet_region" {
  description = "Region of the public subnet."
  type        = string
  default     = ""
}

variable "private_subnet_cidr" {
  description = "Private subnet: everything else."
  type        = string
  default     = "10.0.2.0/24"
}

variable "private_subnet_region" {
  description = "Region of the private subnet."
  type        = string
  default     = ""
}

variable "enable_nat" {
  description = "Create a Cloud NAT so private VMs can reach the internet (apt, pip, docker pulls)."
  type        = bool
  default     = true
}

variable "machine_type_default" {
  description = "Default machine type for VMs without an explicit override."
  type        = string
  default     = "e2-small"
}

variable "boot_disk_image" {
  description = "Boot disk image family used for all VMs."
  type        = string
  default     = "ubuntu-2204-lts"
}

variable "boot_disk_size_gb" {
  description = "Boot disk size in GB."
  type        = number
  default     = 30
}

variable "instances" {
  description = "VM definitions. Keys are hostnames; ip matches the spec section 2 IP plan."
  type = map(object({
    ip             = string
    machine_type   = optional(string)
    boot_disk_size = optional(number)
    tags           = optional(list(string), [])
  }))

  default = {
    ctrl-node    = { ip = "10.0.2.10", tags = ["mgmt"] }
    git-cicd     = { ip = "10.0.2.11", machine_type = "e2-medium", tags = ["mgmt"] }
    k8s-cp       = { ip = "10.0.2.20", machine_type = "e2-medium", tags = ["mgmt", "k8s"] }
    k8s-wk1      = { ip = "10.0.2.21", machine_type = "e2-medium", tags = ["mgmt", "k8s", "public"] }
    k8s-wk2      = { ip = "10.0.2.22", machine_type = "e2-medium", tags = ["mgmt", "k8s", "public"] }
    mlflow       = { ip = "10.0.2.30", machine_type = "e2-medium", tags = ["mgmt"] }
    fastapi      = { ip = "10.0.2.31", tags = ["mgmt", "public"] }
    postgres     = { ip = "10.0.2.40", machine_type = "e2-medium", tags = ["mgmt"] }
    prometheus   = { ip = "10.0.2.50", machine_type = "e2-medium", tags = ["mgmt"] }
    grafana      = { ip = "10.0.2.51", machine_type = "e2-medium", tags = ["mgmt", "public"] }
    training-env = { ip = "10.0.2.60", machine_type = "e2-medium", tags = ["mgmt"] }
    testing-env  = { ip = "10.0.2.61", tags = ["mgmt"] }
  }
}
