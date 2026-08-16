output "instance_ips" {
  description = "Map of hostname -> private IP (spec section 2 IP plan)."
  value       = { for k, v in google_compute_instance.vm : k => v.network_interface[0].network_ip }
}

output "instance_names" {
  description = "Map of hostname -> GCP instance name."
  value       = { for k, v in google_compute_instance.vm : k => v.name }
}

output "instance_ids" {
  description = "Map of hostname -> instance ID."
  value       = { for k, v in google_compute_instance.vm : k => v.id }
}
