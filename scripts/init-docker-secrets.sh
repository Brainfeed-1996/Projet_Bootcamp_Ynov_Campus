#!/bin/bash
# scripts/init-docker-secrets.sh - Initialisation des secrets Docker
# Usage: ./scripts/init-docker-secrets.sh
# Ce script génère des secrets aléatoires pour le développement local.
# En production, utiliser un système de gestion des secrets (Vault, etc.)

set -euo pipefail

SECRETS_DIR="./secrets"

# Vérifier si le répertoire existe déjà
if [ -d "$SECRETS_DIR" ]; then
    echo "ATTENTION: Le répertoire $SECRETS_DIR existe déjà."
    read -p "Voulez-vous le supprimer et recréer ? (o/N) " -r CONFIRM
    if [[ ! "$CONFIRM" =~ ^[Oo]$ ]]; then
        echo "Annulé."
        exit 0
    fi
    rm -rf "$SECRETS_DIR"
fi

echo "Création du répertoire de secrets..."
mkdir -p "$SECRETS_DIR"

# Valider que openssl est disponible
if ! command -v openssl &>/dev/null; then
    echo "ERREUR: openssl est requis pour générer des secrets." >&2
    exit 1
fi

# Générer un seul mot de passe partagé (utilisé par l'application et PostgreSQL)
SHARED_PASSWORD=$(openssl rand -base64 32)

# Écrire les fichiers de manière atomique avec umask 077
umask 077

write_secret() {
    local filename="$1"
    local content="$2"
    local tmpfile="${SECRETS_DIR}/${filename}.tmp"
    printf '%s' "$content" > "$tmpfile"
    mv "$tmpfile" "${SECRETS_DIR}/${filename}"
}

# Mot de passe unique pour db_password.txt et postgres_password.txt
write_secret "db_password.txt" "$SHARED_PASSWORD"
write_secret "postgres_password.txt" "$SHARED_PASSWORD"
write_secret "secret_key.txt" "$(openssl rand -base64 32)"
write_secret "postgres_user.txt" "$(openssl rand -base64 16)"

# Permissions restrictives
chmod 400 "$SECRETS_DIR"/*.txt

# Chown UID 1000 (container user) si possible
if [ "$(id -u)" != "1000" ]; then
    chown 1000:1000 "$SECRETS_DIR"/*.txt 2>/dev/null || true
else
    chown $(id -u):$(id -g) "$SECRETS_DIR"/*.txt 2>/dev/null || true
fi

echo ""
echo "Secrets créés dans $SECRETS_DIR :"
ls -la "$SECRETS_DIR"
echo ""
echo "N'oubliez pas de :
- Ajouter $SECRETS_DIR/ dans .gitignore
- Ne jamais commit ces fichiers
- Supprimer ces fichiers avant le déploiement en production"