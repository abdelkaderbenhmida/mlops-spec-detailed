variable "network_id" {
  description = "Self-link of the VPC the firewall rules apply to."
  type        = string
}

variable "private_cidr" {
  description = "Private subnet CIDR (10.0.2.0/24) used by sg-internal and sg-k8s."
  type        = string
}

variable "admin_ip" {
  description = "Admin IP CIDR allowed SSH access via sg-mgmt (e.g. 203.0.113.10/32)."
  type        = string
}

variable "mgmt_tags" {
  description = "Network tags matched by sg-mgmt (SSH from admin IP)."
  type        = list(string)
  default     = ["mgmt"]
}

variable "internal_tags" {
  description = "Network tags matched by sg-internal (all traffic inside the private subnet)."
  type        = list(string)
  default     = ["mgmt"]
}

variable "k8s_tags" {
  description = "Network tags matched by sg-k8s (Kubernetes control-plane/worker ports)."
  type        = list(string)
  default     = ["k8s"]
}

variable "public_tags" {
  description = "Network tags matched by sg-public (80/443 from the internet)."
  type        = list(string)
  default     = ["public"]
}
