locals {
  ssh_user = split(":", split("@", split(" ", trimspace(file(var.ssh_public_key)))[2])[0])[0]
}

# ---------------------------------------------------------------------------
# 12 VMs with static private IPs per the spec section 2 IP plan.
# Static internal IPs (google_compute_address, purpose GCE_ENDPOINT) guarantee
# the exact 10.0.2.x addresses the Ansible inventory depends on.
# ---------------------------------------------------------------------------
resource "google_compute_address" "static_ip" {
  for_each = var.instances

  name         = "${each.key}-ip"
  project      = var.project_id
  region       = var.region
  address_type = "INTERNAL"
  purpose      = "GCE_ENDPOINT"
  subnetwork   = var.subnetwork_id
  address      = each.value.ip
}

resource "google_compute_instance" "vm" {
  for_each = var.instances

  name         = each.key
  machine_type = coalesce(each.value.machine_type, var.machine_type_default)
  zone         = var.zone

  tags = each.value.tags

  boot_disk {
    initialize_params {
      image = var.boot_disk_image
      size  = coalesce(each.value.boot_disk_size, var.boot_disk_size_gb)
    }
  }

  network_interface {
    network    = var.network_id
    subnetwork = var.subnetwork_id
    network_ip = google_compute_address.static_ip[each.key].address
  }

  metadata = {
    ssh-keys = "${local.ssh_user}:${trimspace(file(var.ssh_public_key))}"
  }

  service_account {
    scopes = ["cloud-platform"]
  }
}
