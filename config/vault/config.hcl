listener "tcp" {
  address = "0.0.0.0:8200"
  tls_cert_file = "/vault/tls/vault.crt"
  tls_key_file = "/vault/tls/vault.key"
}

storage "file" {
  path = "/vault/data"
}

default_lease_duration = "24h"
max_lease_duration = "24h"

path "secret/music-hall/*" {
  capabilities = ["create", "read", "update", "delete"]
}

path "secret/music-hall" {
  capabilities = ["list"]
}

# Dynamic secrets for database
path "dynamic/db-credentials/music-hall" {
  capabilities = ["read"]
  parameters = {
    ttl = "1h"
    max_ttl = "24h"
  }
}

# Enable audit logging
path "/sys/audit" {
  capabilities = ["create", "update"]
}

# Audit device configuration
audit_device file {
  file_path = "/var/log/vault_audit.log"
}

# Audit logging policies
path "sys/audit" {
  capabilities = ["create", "update"]
}

# Audit device
audit_device file {
  file_path = "/var/log/vault_audit.log"
  description = "File audit device"
}
