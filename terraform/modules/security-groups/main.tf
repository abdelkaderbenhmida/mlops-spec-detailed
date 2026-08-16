# ---------------------------------------------------------------------------
# Security groups -> GCP firewall rules (spec section 2)
#
#   sg-mgmt     : 22 from admin IP (tags: mgmt)
#   sg-internal : all traffic within 10.0.2.0/24 (tags: mgmt)
#   sg-k8s      : 6443/2379-2380/10250-10259/NodePort, internal only (tags: k8s)
#   sg-public   : 80/443 from internet, forwards to Ingress NodePort / LB (tags: public)
# ---------------------------------------------------------------------------

resource "google_compute_firewall" "sg_mgmt" {
  name        = "sg-mgmt"
  network     = var.network_id
  description = "SSH (22) from the admin IP only."

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = [var.admin_ip]
  target_tags   = var.mgmt_tags
}

resource "google_compute_firewall" "sg_internal" {
  name        = "sg-internal"
  network     = var.network_id
  description = "All traffic within the private subnet (10.0.2.0/24)."

  allow {
    protocol = "tcp"
  }
  allow {
    protocol = "udp"
  }
  allow {
    protocol = "icmp"
  }

  source_ranges = [var.private_cidr]
  target_tags   = var.internal_tags
}

resource "google_compute_firewall" "sg_k8s" {
  name        = "sg-k8s"
  network     = var.network_id
  description = "Kubernetes control-plane/worker ports, internal only."

  allow {
    protocol = "tcp"
    ports    = ["6443", "2379-2380", "10250-10259", "30000-32767"]
  }

  source_ranges = [var.private_cidr]
  target_tags   = var.k8s_tags
}

resource "google_compute_firewall" "sg_public" {
  name        = "sg-public"
  network     = var.network_id
  description = "HTTP/HTTPS from the internet, forwards to the Ingress NodePort / LB."

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = var.public_tags
}
