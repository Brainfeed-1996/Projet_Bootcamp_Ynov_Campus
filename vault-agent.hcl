# vault-agent.hcl - Vault Agent Configuration
# Place this file at /etc/vault-agent.hcl on the target host

pid_file = "/tmp/vault-agent.pid"

# Database credentials template
template {
  source      = "/etc/templates/db-credentials.env.tmpl"
  destination = "/run/secrets/db-credentials.env"
  command      = "systemctl reload music-hall"
}

# Secret key template
template {
  source      = "/etc/templates/secret-key.env.tmpl"
  destination = "/run/secrets/secret-key.env"
}

# Vault server configuration
auto_auth {
  method "kubernetes" {
    config = {
      role = "music-hall"
    }
  }

  sink {
    file {
      path = "/tmp/vault-token"
    }
  }
}

# KV v2 secrets engine path
secret_path = "secret/data/music-hall"