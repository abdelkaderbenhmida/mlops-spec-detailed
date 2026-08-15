resource "google_compute_network" "vpc" {
  name                    = var.vpc_name
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "public" {
  name                     = "${var.vpc_name}-public"
  network                  = google_compute_network.vpc.id
  region                   = var.region
  ip_cidr_range            = var.public_subnet_cidr
  private_ip_google_access = true
}

resource "google_compute_subnetwork" "private" {
  name                     = "${var.vpc_name}-private"
  network                  = google_compute_network.vpc.id
  region                   = var.region
  ip_cidr_range            = var.private_subnet_cidr
  private_ip_google_access = true
}

resource "google_compute_router" "nat_router" {
  count   = var.enable_nat ? 1 : 0
  name    = "${var.vpc_name}-nat-router"
  region  = var.region
  network = google_compute_network.vpc.id
}

resource "google_compute_router_nat" "nat" {
  count                              = var.enable_nat ? 1 : 0
  name                               = "${var.vpc_name}-nat"
  router                             = google_compute_router.nat_router[0].name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"
  subnetwork {
    name                    = google_compute_subnetwork.private.id
    source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
  }
}
