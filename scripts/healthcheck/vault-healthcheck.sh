#!/bin/bash
# scripts/healthcheck/vault-healthcheck.sh - Vault health check
# Used by Docker healthcheck for the Vault service
# Returns 0 on success, 1 on failure

set -euo pipefail

VAULT_ADDR="${VAULT_ADDR:-http://localhost:8200}"
TIMEOUT="${HEALTHCHECK_TIMEOUT:-5}"
MAX_RETRIES="${HEALTHCHECK_RETRIES:-3}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

check_vault_status() {
    local retries=0
    while [ $retries -lt $MAX_RETRIES ]; do
        if vault status -address="$VAULT_ADDR" >/dev/null 2>&1; then
            log "Vault health check passed"
            return 0
        fi
        retries=$((retries + 1))
        if [ $retries -lt $MAX_RETRIES ]; then
            log "Vault health check failed, retrying ($retries/$MAX_RETRIES)..."
            sleep 1
        fi
    done
    log "Vault health check failed after $MAX_RETRIES attempts"
    return 1
}

check_vault_sealed() {
    local status
    status=$(vault status -address="$VAULT_ADDR" -format=json 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('sealed', True))" 2>/dev/null || echo "true")
    if [ "$status" = "false" ]; then
        log "Vault is unsealed"
        return 0
    fi
    log "Vault is sealed"
    return 1
}

main() {
    log "Starting Vault health check for $VAULT_ADDR"
    check_vault_status
    check_vault_sealed
}

main "$@"