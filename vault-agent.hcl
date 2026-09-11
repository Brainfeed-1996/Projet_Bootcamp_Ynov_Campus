# vault-agent.hcl - Configuration Vault Agent
# Place this file at /etc/vault-agent.hcl on the target host

pid_file = "/tmp/vault-agent.pid"

# Template pour les secrets de la base de données
template {
  source      = "/etc/templates/db-credentials.env.tmpl"
  destination = "/run/secrets/db-credentials.env"
  command      = "systemctl restart music-hall"
}

# Template pour la clé secrète
template {
  source      = "/etc/templates/secret-key.env.tmpl"
  destination = "/run/secrets/secret-key.env"
}

# Configuration du serveur Vault
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

# Moteur de secrets KV v2
secret_path = "secret/data/music-hall"