# Configuration Vault de base
# Ce fichier est monté dans le conteneur Vault à /vault/config

storage "file" {
  path = "/vault/data"
}

listener "tcp" {
  address = "0.0.0.0:8200"
  tls_disable = 1
}

# Désactiver le logging des secrets
default_lease_duration = "24h"
max_lease_duration = "24h"