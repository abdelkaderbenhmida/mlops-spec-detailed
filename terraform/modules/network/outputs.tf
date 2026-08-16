output "network_id" {
  description = "Self-link of the VPC."
  value       = google_compute_network.vpc.id
}

output "network_name" {
  description = "Name of the VPC."
  value       = google_compute_network.vpc.name
}

output "public_subnet_id" {
  description = "Self-link of the public subnet."
  value       = google_compute_subnetwork.public.id
}

output "private_subnet_id" {
  description = "Self-link of the private subnet."
  value       = google_compute_subnetwork.private.id
}

output "nat_name" {
  description = "Name of the Cloud NAT (empty when disabled)."
  value       = var.enable_nat ? google_compute_router_nat.nat[0].name : ""
}
