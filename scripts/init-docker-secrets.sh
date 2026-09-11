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

echo "Génération des secrets aléatoires..."
openssl rand -base64 32 > "$SECRETS_DIR/db_password.txt"
openssl rand -base64 32 > "$SECRETS_DIR/secret_key.txt"
openssl rand -base64 16 > "$SECRETS_DIR/postgres_user.txt"
openssl rand -base64 32 > "$SECRETS_DIR/postgres_password.txt"

# Permissions restrictives
chmod 400 "$SECRETS_DIR"/*.txt
chown $(id -u):$(id -g) "$SECRETS_DIR"/*.txt 2>/dev/null || true

echo ""
echo "Secrets créés dans $SECRETS_DIR :"
ls -la "$SECRETS_DIR"
echo ""
echo "N'oubliez pas de :
- Ajouter $SECRETS_DIR/ dans .gitignore
- Ne jamais commit ces fichiers
- Supprimer ces fichiers avant le déploiement en production"