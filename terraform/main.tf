provider "google" {
  project = var.project_id
  region  = var.region
}

# ---------------------------------------------------------------------------
# Network: VPC 10.0.0.0/16, public subnet 10.0.1.0/24, private subnet 10.0.2.0/24
# ---------------------------------------------------------------------------
module "network" {
  source = "./modules/network"

  vpc_name            = var.vpc_name
  vpc_cidr            = var.vpc_cidr
  region              = var.region
  public_subnet_cidr  = var.public_subnet_cidr
  private_subnet_cidr = var.private_subnet_cidr
  enable_nat          = var.enable_nat
}

# ---------------------------------------------------------------------------
# Security groups -> GCP firewall rules (spec section 2)
# ---------------------------------------------------------------------------
module "security_groups" {
  source = "./modules/security-groups"

  network_id    = module.network.network_id
  private_cidr  = var.private_subnet_cidr
  admin_ip      = var.admin_ip
  mgmt_tags     = ["mgmt"]
  internal_tags = ["mgmt"]
  k8s_tags      = ["k8s"]
  public_tags   = ["public"]
}

# ---------------------------------------------------------------------------
# Compute: 12 VMs with static private IPs per spec section 2
# ---------------------------------------------------------------------------
module "compute" {
  source = "./modules/compute"

  project_id           = var.project_id
  region               = var.region
  zone                 = var.zone
  network_id           = module.network.network_id
  subnetwork_id        = module.network.private_subnet_id
  ssh_public_key       = var.ssh_public_key
  instances            = var.instances
  machine_type_default = var.machine_type_default
  boot_disk_image      = var.boot_disk_image
  boot_disk_size_gb    = var.boot_disk_size_gb
}
