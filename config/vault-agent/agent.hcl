# Configuration Vault Agent
# This file is mounted in the vault-agent container at /etc/vault-agent

pid_file = "/tmp/vault-agent.pid"

vault {
  addr = "http://vault:8200"
}

auto_auth {
  method "token" {
    config = {
      token_file = "/tmp/vault-token"
    }
  }
}

template {
  destination = "/run/secrets/db_password.txt"
  contents = "{{ with secret \"secret/music-hall\" }}{{ .Data.data.db_password }}{{ end }}"
}

template {
  destination = "/run/secrets/secret_key.txt"
  contents = "{{ with secret \"secret/music-hall\" }}{{ .Data.data.secret_key }}{{ end }}"
}

template {
  destination = "/run/secrets/postgres_user.txt"
  contents = "{{ with secret \"secret/music-hall\" }}{{ .Data.data.postgres_user }}{{ end }}"
}

template {
  destination = "/run/secrets/postgres_password.txt"
  contents = "{{ with secret \"secret/music-hall\" }}{{ .Data.data.postgres_password }}{{ end }}"
}

template {
  destination = "/run/secrets/openai_api_key.txt"
  contents = "{{ with secret \"secret/music-hall\" }}{{ .Data.data.openai_api_key }}{{ end }}"
}

retry {
  attempts = 5
  backoff {
    duration = "5s"
    max_duration = "60s"
  }
}