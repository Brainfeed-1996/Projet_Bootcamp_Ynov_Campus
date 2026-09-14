#!/bin/bash
# scripts/vault-init.sh - Initialisation des secrets dans Vault
# Usage: ./scripts/vault-init.sh
# Ce script est OPTIONNEL - il initialise des secrets dans un instance Vault
# Doit être exécuté manuellement après le déploiement de Vault.
# Les secrets ne sont JAMAIS affichés dans les logs.

set -euo pipefail

# Configuration
VAULT_ADDR="${VAULT_ADDR:-http://vault:8200}"
VAULT_ROLE_ID="${VAULT_ROLE_ID:-}"
VAULT_SECRET_ID="${VAULT_SECRET_ID:-}"
KV_MOUNT="${VAULT_KV_MOUNT:-secret}"
SECRETS_PATH="music-hall"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifications de sécurité
if [ -z "$VAULT_ROLE_ID" ] || [ -z "$VAULT_SECRET_ID" ]; then
    log_error "VAULT_ROLE_ID et/ou VAULT_SECRET_ID non défini(s)."
    echo "Définissez-les avec les identifiants AppRole de Vault."
    echo "Ex: export VAULT_ROLE_ID='xxxxx' && export VAULT_SECRET_ID='xxxxx'"
    exit 1
fi

# Vérifier que les identifiants ne sont pas exposés dans l'environnement
if [ -t 0 ]; then
    log_warn "Ce script va créer des secrets dans Vault."
    read -p "Continuer ? (o/N) " -r CONFIRM
    if [[ ! "$CONFIRM" =~ ^[Oo]$ ]]; then
        echo "Annulé."
        exit 0
    fi
fi

export VAULT_ADDR="$VAULT_ADDR"

log_info "Authentification à Vault via AppRole..."
if ! vault write auth/approle/login role_id="$VAULT_ROLE_ID" secret_id="$VAULT_SECRET_ID" -field=client_token > /tmp/vault-token 2>/dev/null; then
    log_error "Impossible de s'authentifier à Vault à $VAULT_ADDR via AppRole."
    echo "Vérifiez vos identifiants AppRole et que Vault est démarré."
    exit 1
fi
export VAULT_TOKEN="$(cat /tmp/vault-token)"
rm -f /tmp/vault-token

log_info "Initialisation des secrets dans Vault à $VAULT_ADDR..."

# Vérifier la connexion à Vault
if ! vault status >/dev/null 2>&1; then
    log_error "Impossible de se connecter à Vault à $VAULT_ADDR"
    echo "Vérifiez que Vault est démarré et que l'authentification est valide."
    exit 1
fi

# Activer le moteur KV v2 si nécessaire
log_info "Activation du moteur KV v2..."
vault secrets enable -path="$KV_MOUNT" kv-v2 2>/dev/null || \
    log_info "Le moteur KV v2 est déjà activé à $KV_MOUNT."

# Génération des secrets aléatoires (non affichés)
DB_USER="${DB_USER:-appuser}"
DB_PASSWORD="$(openssl rand -base64 32)"
SECRET_KEY="$(openssl rand -base64 32)"
POSTGRES_USER="${POSTGRES_USER:-appuser}"
POSTGRES_PASSWORD="$(openssl rand -base64 32)"
POSTGRES_DB="${POSTGRES_DB:-music_hall}"
OPENAI_API_KEY="${OPENAI_API_KEY:-sk-proj-default-key}"
JWT_EXPIRATION="3600"

log_info "Stockage des secrets dans Vault (chemin: $KV_MOUNT/$SECRETS_PATH)..."

# Stockage des secrets - les valeurs ne sont pas affichées
vault kv put -mount="$KV_MOUNT" "$KV_MOUNT/$SECRETS_PATH" \
    db_user="$DB_USER" \
    db_password="$DB_PASSWORD" \
    secret_key="$SECRET_KEY" \
    postgres_user="$POSTGRES_USER" \
    postgres_password="$POSTGRES_PASSWORD" \
    postgres_db="$POSTGRES_DB" \
    openai_api_key="$OPENAI_API_KEY" \
    jwt_expiration="$JWT_EXPIRATION"

log_info "Secrets créés avec succès dans Vault."
echo "Chemin: $KV_MOUNT/$SECRETS_PATH"

# Ne JAMAIS afficher les valeurs des secrets
log_info "Vérification de la structure (sans afficher les valeurs)..."
vault kv get -mount="$KV_MOUNT" "$KV_MOUNT/$SECRETS_PATH" --format=json 2>/dev/null | \
    python3 -c "import sys,json; d=json.load(sys.stdin); print('Clés stockées:', list(d.get('data',{}).get('data',{}).keys()))" 2>/dev/null || \
    log_warn "Vérifiez manuellement la structure dans Vault."

echo ""
echo "Limites :"
echo "- Ce script est optionnel et doit être exécuté manuellement"
echo "- Les secrets sont stockés dans Vault, pas dans les fichiers"
echo "- Les identifiants AppRole doivent avoir les permissions appropriées"
echo "- En production, utiliser un système de gestion des secrets centralisé"
# Renouveler le token Vault
vault token renew -increment=3600 2>/dev/null || true

# V�rifier la validit� du token
if ! vault token lookup -field=expire_time 2>/dev/null; then
    echo 'Token Vault expir�, re-authentification requise'
    exit 1
fi
