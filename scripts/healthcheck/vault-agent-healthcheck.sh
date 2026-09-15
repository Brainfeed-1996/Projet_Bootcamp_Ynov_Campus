#!/bin/bash
# scripts/healthcheck/vault-agent-healthcheck.sh - Vault Agent health check
# Used by Docker healthcheck for the Vault Agent service
# Returns 0 on success, 1 on failure

set -euo pipefail

SECRETS_DIR="${VAULT_SECRETS_DIR:-/run/secrets}"
REQUIRED_SECRETS=("db_password.txt" "secret_key.txt" "postgres_user.txt" "postgres_password.txt" "openai_api_key.txt")
TIMEOUT="${HEALTHCHECK_TIMEOUT:-5}"
MAX_RETRIES="${HEALTHCHECK_RETRIES:-3}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

check_secrets_exist() {
    local missing=0
    for secret in "${REQUIRED_SECRETS[@]}"; do
        if [ ! -f "$SECRETS_DIR/$secret" ]; then
            log "Missing secret: $secret"
            missing=1
        elif [ ! -s "$SECRETS_DIR/$secret" ]; then
            log "Empty secret: $secret"
            missing=1
        fi
    done
    if [ $missing -eq 0 ]; then
        log "All required secrets present"
        return 0
    fi
    return 1
}

check_vault_agent_process() {
    if pgrep -f "vault agent" >/dev/null 2>&1; then
        log "Vault agent process running"
        return 0
    fi
    log "Vault agent process not found"
    return 1
}

main() {
    log "Starting Vault Agent health check"
    check_vault_agent_process
    check_secrets_exist
}

main "$@"