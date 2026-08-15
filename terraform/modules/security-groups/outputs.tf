output "firewall_names" {
  description = "Names of all firewall rules created."
  value = [
    google_compute_firewall.sg_mgmt.name,
    google_compute_firewall.sg_internal.name,
    google_compute_firewall.sg_k8s.name,
    google_compute_firewall.sg_public.name,
  ]
}

output "sg_mgmt_name" {
  value = google_compute_firewall.sg_mgmt.name
}

output "sg_internal_name" {
  value = google_compute_firewall.sg_internal.name
}

output "sg_k8s_name" {
  value = google_compute_firewall.sg_k8s.name
}

output "sg_public_name" {
  value = google_compute_firewall.sg_public.name
}
