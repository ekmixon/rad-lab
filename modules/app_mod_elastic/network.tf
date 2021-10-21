/**
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

module "elastic_search_network" {
  source  = "terraform-google-modules/network/google"
  version = "~> 3.0"

  project_id   = module.elastic_search_project.project_id
  network_name = var.network_name
  routing_mode = "GLOBAL"
  description  = "VPC Network created via Terraform"

  subnets = [
    {
      subnet_name           = var.subnet_name
      subnet_ip             = var.network_cidr_block
      subnet_region         = var.region
      description           = "Subnetwork inside ${var.network_name} VPC network, created via Terraform"
      subnet_private_access = true

    }
  ]

  secondary_ranges = {
    "${var.subnet_name}" = [{ # Do not remove quotes, Terraform doesn't like variable references as map-keys without them
      range_name    = local.pod_range_name
      ip_cidr_range = var.pod_cidr_block
      }, {
      range_name    = local.service_range_name
      ip_cidr_range = var.service_cidr_block
    }]
  }
}

// External access
resource "google_compute_router" "router" {
  count = var.enable_internet_egress_traffic ? 1 : 0

  project = module.elastic_search_project.project_id
  name    = "es-access-router"
  network = module.elastic_search_network.network_self_link
  region  = var.region

  bgp {
    asn = 64514
  }
}

resource "google_compute_router_nat" "nat" {
  count                              = var.enable_internet_egress_traffic ? 1 : 0
  project                            = module.elastic_search_project.project_id
  name                               = "es-proxy-ext-access-nat"
  router                             = google_compute_router.router[0].name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

resource "google_compute_route" "external_access" {
  count            = var.enable_internet_egress_traffic ? 1 : 0
  project          = module.elastic_search_project.project_id
  dest_range       = "0.0.0.0/0"
  name             = "proxy-external-access"
  network          = module.elastic_search_network.network_name
  next_hop_gateway = "default-internet-gateway"
}
