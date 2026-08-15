output "vpc_name" {
  description = "Name of the created VPC."
  value       = module.network.network_name
}

output "public_subnet" {
  description = "Public subnet self-link."
  value       = module.network.public_subnet_id
}

output "private_subnet" {
  description = "Private subnet self-link."
  value       = module.network.private_subnet_id
}

output "instance_ips" {
  description = "Map of hostname -> private IP for every VM (spec section 2)."
  value       = module.compute.instance_ips
}

output "instance_names" {
  description = "Map of hostname -> GCP instance name."
  value       = module.compute.instance_names
}
