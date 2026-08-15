variable "vpc_name" {
  description = "Name of the VPC."
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR block."
  type        = string
}

variable "region" {
  description = "GCP region for subnets and NAT."
  type        = string
}

variable "public_subnet_cidr" {
  description = "Public subnet CIDR (ingress/LB entrypoint only)."
  type        = string
}

variable "private_subnet_cidr" {
  description = "Private subnet CIDR (everything else)."
  type        = string
}

variable "enable_nat" {
  description = "Create a Cloud NAT so private VMs can reach the internet."
  type        = bool
  default     = true
}
