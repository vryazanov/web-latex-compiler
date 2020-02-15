# Common
terraform {
  backend "gcs" {
    bucket      = "web-latex-compiler-tf-state"
    prefix      = "terraform/state"
    credentials = var.gc_dredentials
  }
}

resource "random_id" "instance_id" {
  byte_length = 4
}

resource "random_id" "db_name_suffix" {
  byte_length = 4
}

provider "google" {
  credentials = var.gc_dredentials
  project     = var.project_id
}

data "google_dns_managed_zone" "env_dns_zone" {
  name = "web-latex-compiler"
}

data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

# VPC and network
resource "google_compute_network" "vpc_network" {
  name = "vpc-network"
}

resource "google_compute_global_address" "private_ip_address" {
  name          = "private-ip-address"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc_network.self_link
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc_network.self_link
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

resource "google_compute_firewall" "out" {
  name      = "allow-out"
  direction = "EGRESS"
  network   = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
  }

  allow {
    protocol = "udp"
  }
}

resource "google_compute_firewall" "in" {
  name      = "allow-in"
  direction = "INGRESS"
  network   = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
  }

  allow {
    protocol = "udp"
  }
}


# Google run
resource "google_cloud_run_service" "web" {
  name          = "web-latex-compiler"
  location      = "us-central1"

  template {
    spec {
      containers {
        image   = "eu.gcr.io/web-latex-compiler-262817/web:master"

        env {
          name  = "FLASK_CONFIG"
          value = "web.configs.cloud.CloudConfig"
        }
        env {
          name  = "SQLALCHEMY_DATABASE_URI"
          value = "postgres://${var.database_user}:${var.database_password}@/${google_sql_database.db.name}?host=/cloudsql/${var.project_id}:us-central1:${google_sql_database_instance.db_instance.name}"
        }
        env {
          name  = "GC_PROJECT"
          value = var.project_id
        }
        env {
          name  = "GC_TOPIC"
          value = google_pubsub_topic.pdf_topic.name
        }
        env {
          name  = "GC_SUBSCRIPTION"
          value = google_pubsub_subscription.pdf_subscription.name
        }
        env {
          name  = "GC_STORAGE"
          value = google_storage_bucket.main_bucket.name
        }
      }
    }

    metadata {
      namespace = var.project_id
      annotations = {
        "run.googleapis.com/cloudsql-instances" = "${var.project_id}:us-central1:${google_sql_database_instance.db_instance.name}",
        "run.googleapis.com/client-name"        = "cloud-console"
      }
    }

  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_policy" "noauth" {
  location    = google_cloud_run_service.web.location
  project     = google_cloud_run_service.web.project
  service     = google_cloud_run_service.web.name
  policy_data = data.google_iam_policy.noauth.policy_data
}

resource "google_cloud_run_domain_mapping" "web" {
  location = "us-central1"
  name     =  "compile-latex.online"

  metadata {
    namespace = var.project_id
  }

  spec {
    route_name = google_cloud_run_service.web.name
  }
}

# Database
resource "google_sql_database" "db" {
  name     = "web-latex-compiler"
  instance = google_sql_database_instance.db_instance.name
}

resource "google_sql_database_instance" "db_instance" {
  name             = "web-latex-compiler-db-f1-${random_id.db_name_suffix.hex}"
  database_version = "POSTGRES_11"
  region           = "us-central1"
  depends_on       = [google_service_networking_connection.private_vpc_connection]

  settings {
    tier = "db-f1-micro"

    ip_configuration {
      ipv4_enabled = true
      private_network = google_compute_network.vpc_network.self_link
    }
  }
}

resource "google_sql_user" "users" {
  instance = google_sql_database_instance.db_instance.name
  name     = var.database_user
  password = var.database_password
}

# Worker
resource "google_compute_instance" "default" {
  name         = "web-latex-compiler-worker-${random_id.instance_id.hex}"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      size = 20
      image = "ubuntu-1804-lts"
    }
  }

  metadata_startup_script = <<EOT
    sudo apt-get update

    sudo apt-get install -y \
      apt-transport-https \
      ca-certificates \
      curl \
      gnupg-agent \
      software-properties-common
    
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

    sudo add-apt-repository \
      "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) \
      stable"

    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io

    sudo echo '${file(".secrets/credentials.json")}' > ~/google-cloud-credentials.json
    sudo cat /root/google-cloud-credentials.json | sudo docker login -u _json_key --password-stdin https://eu.gcr.io
    sudo docker pull eu.gcr.io/web-latex-compiler-262817/worker:master

    sudo docker run \
      --network host \
      -e GOOGLE_APPLICATION_CREDENTIALS=/google-cloud-credentials.json \
      -e FLASK_CONFIG=web.configs.cloud.CloudConfig \
      -e SQLALCHEMY_DATABASE_URI=postgres://${var.database_user}:${var.database_password}@${google_sql_database_instance.db_instance.private_ip_address}/${google_sql_database.db.name} \
      -e GC_PROJECT=${var.project_id} \
      -e GC_TOPIC=${google_pubsub_topic.pdf_topic.name} \
      -e GC_SUBSCRIPTION=${google_pubsub_subscription.pdf_subscription.name} \
      -e GC_STORAGE=${google_storage_bucket.main_bucket.name} \
      -v ~/google-cloud-credentials.json:/google-cloud-credentials.json \
      eu.gcr.io/web-latex-compiler-262817/worker:master pubsub listen --sleep 5 --batch-size 5
    EOT

  network_interface {
    network = google_compute_network.vpc_network.self_link

    access_config {
      // Ephemeral IP
    }
  }
}

# Storage
resource "google_storage_bucket" "main_bucket" {
  name     = "web-latex-compiler-files"
  location = "EU"
}

# Pub / Sub
resource "google_pubsub_topic" "pdf_topic" {
  name = "pdf-topic"
}

resource "google_pubsub_subscription" "pdf_subscription" {
  name  = "pdf-subscription"
  topic = google_pubsub_topic.pdf_topic.name

  message_retention_duration = "1200s"
  retain_acked_messages      = true

  ack_deadline_seconds = 20

  expiration_policy {
    ttl = "300000.5s"
  }
}

# DNS records
locals {
  dns_A = [
    for record in google_cloud_run_domain_mapping.web.status[0].resource_records:
      record.rrdata if record.type == "A"
  ]
  dns_AAAA = [
    for record in google_cloud_run_domain_mapping.web.status[0].resource_records:
      record.rrdata if record.type == "AAAA"
  ]
  dns_CNAME = [
    for record in google_cloud_run_domain_mapping.web.status[0].resource_records:
      record.rrdata if record.type == "CNAME"    
  ]
}

resource "google_dns_record_set" "dns_A" {
  name          = data.google_dns_managed_zone.env_dns_zone.dns_name
  type          = "A"
  ttl           = 300
  managed_zone  = data.google_dns_managed_zone.env_dns_zone.name
  rrdatas       = local.dns_A
  count         = length(local.dns_A) == 0 ? 0 : 1
}

resource "google_dns_record_set" "dns_AAAA" {
  name          = data.google_dns_managed_zone.env_dns_zone.dns_name
  type          = "AAAA"
  ttl           = 300
  managed_zone  = data.google_dns_managed_zone.env_dns_zone.name
  rrdatas       = local.dns_AAAA
  count         = length(local.dns_AAAA) == 0 ? 0 : 1
}

resource "google_dns_record_set" "dns_CNAME" {
  name          = data.google_dns_managed_zone.env_dns_zone.dns_name
  type          = "CNAME"
  ttl           = 300
  managed_zone  = data.google_dns_managed_zone.env_dns_zone.name
  rrdatas       = local.dns_CNAME
  count         = length(local.dns_CNAME) == 0 ? 0 : 1
}
