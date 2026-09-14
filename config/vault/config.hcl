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
