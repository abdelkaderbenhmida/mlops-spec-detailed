variable "project_id" {
  description = "GCP project ID."
  type        = string
}

variable "region" {
  description = "GCP region for the static IP addresses."
  type        = string
}

variable "zone" {
  description = "GCP zone for compute instances."
  type        = string
}

variable "network_id" {
  description = "Self-link of the VPC."
  type        = string
}

variable "subnetwork_id" {
  description = "Self-link of the private subnetwork (10.0.2.0/24)."
  type        = string
}

variable "ssh_public_key" {
  description = "Path to the SSH public key file injected into every VM."
  type        = string
}

variable "instances" {
  description = "Map of hostname -> instance definition (ip, machine_type, disk, tags)."
  type = map(object({
    ip             = string
    machine_type   = optional(string)
    boot_disk_size = optional(number)
    tags           = optional(list(string), [])
  }))
}

variable "machine_type_default" {
  description = "Default machine type when not overridden per instance."
  type        = string
  default     = "e2-small"
}

variable "boot_disk_image" {
  description = "Boot disk image family."
  type        = string
  default     = "ubuntu-2204-lts"
}

variable "boot_disk_size_gb" {
  description = "Default boot disk size in GB."
  type        = number
  default     = 30
}
