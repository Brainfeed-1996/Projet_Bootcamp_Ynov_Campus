#!/bin/bash
# scripts/vault-init.sh - Initialize secrets in Vault
# Usage: ./scripts/vault-init.sh
# This script is OPTIONAL - it initializes secrets in a Vault instance
# Must be executed manually after Vault deployment.
# Secrets are NEVER displayed in logs.

set -euo pipefail

# Configuration
VAULT_ADDR="${VAULT_ADDR:-http://vault:8200}"
VAULT_ROLE_ID="${VAULT_ROLE_ID:-}"
VAULT_SECRET_ID="${VAULT_SECRET_ID:-}"
KV_MOUNT="${VAULT_KV_MOUNT:-secret}"
SECRETS_PATH="music-hall"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Security checks
if [ -z "$VAULT_ROLE_ID" ] || [ -z "$VAULT_SECRET_ID" ]; then
    log_error "VAULT_ROLE_ID and/or VAULT_SECRET_ID not set."
    echo "Set them with Vault AppRole credentials."
    echo "Example: export VAULT_ROLE_ID='xxxxx' && export VAULT_SECRET_ID='xxxxx'"
    exit 1
fi

# Verify credentials are not exposed in environment
if [ -t 0 ]; then
    log_warn "This script will create secrets in Vault."
    read -p "Continue? (y/N) " -r CONFIRM
    if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

export VAULT_ADDR="$VAULT_ADDR"

log_info "Authenticating to Vault via AppRole..."
if ! vault write auth/approle/login role_id="$VAULT_ROLE_ID" secret_id="$VAULT_SECRET_ID" -field=client_token > /tmp/vault-token 2>/dev/null; then
    log_error "Failed to authenticate to Vault at $VAULT_ADDR via AppRole."
    echo "Verify your AppRole credentials and that Vault is running."
    exit 1
fi
export VAULT_TOKEN="$(cat /tmp/vault-token)"
rm -f /tmp/vault-token

log_info "Initializing secrets in Vault at $VAULT_ADDR..."

# Verify Vault connection
if ! vault status >/dev/null 2>&1; then
    log_error "Cannot connect to Vault at $VAULT_ADDR"
    echo "Verify Vault is running and authentication is valid."
    exit 1
fi

# Enable KV v2 engine if needed
log_info "Enabling KV v2 engine..."
vault secrets enable -path="$KV_MOUNT" kv-v2 2>/dev/null || \
    log_info "KV v2 engine already enabled at $KV_MOUNT."

# Generate random secrets (not displayed)
DB_USER="${DB_USER:-appuser}"
DB_PASSWORD="$(openssl rand -base64 32)"
SECRET_KEY="$(openssl rand -base64 32)"
POSTGRES_USER="${POSTGRES_USER:-appuser}"
POSTGRES_PASSWORD="$(openssl rand -base64 32)"
POSTGRES_DB="${POSTGRES_DB:-music_hall}"
OPENAI_API_KEY="${OPENAI_API_KEY:-}"
JWT_EXPIRATION="3600"

log_info "Storing secrets in Vault (path: $KV_MOUNT/$SECRETS_PATH)..."

# Store secrets - values are not displayed
vault kv put -mount="$KV_MOUNT" "$KV_MOUNT/$SECRETS_PATH" \
    db_user="$DB_USER" \
    db_password="$DB_PASSWORD" \
    secret_key="$SECRET_KEY" \
    postgres_user="$POSTGRES_USER" \
    postgres_password="$POSTGRES_PASSWORD" \
    postgres_db="$POSTGRES_DB" \
    openai_api_key="$OPENAI_API_KEY" \
    jwt_expiration="$JWT_EXPIRATION"

log_info "Secrets created successfully in Vault."
echo "Path: $KV_MOUNT/$SECRETS_PATH"

# Never display secret values
log_info "Verifying structure (without showing values)..."
vault kv get -mount="$KV_MOUNT" "$KV_MOUNT/$SECRETS_PATH" --format=json 2>/dev/null | \
    python3 -c "import sys,json; d=json.load(sys.stdin); print('Keys stored:', list(d.get('data',{}).get('data',{}).keys()))" 2>/dev/null || \
    log_warn "Verify structure manually in Vault."

echo ""
echo "Notes:"
echo "- This script is optional and must be run manually"
echo "- Secrets are stored in Vault, not in files"
echo "- AppRole credentials must have appropriate permissions"
echo "- In production, use a centralized secrets management system"
# Renew Vault token
vault token renew -increment=3600 2>/dev/null || true

# Verify token validity
if ! vault token lookup -field=expire_time 2>/dev/null; then
    echo 'Vault token expired, re-authentication required'
    exit 1
fi