#!/bin/bash
# ---------------------------------------------------------------------------
# demo-commands.sh
# Commandes de démonstration pré-testées pour le Demo Day — Music Hall
# Compatible Linux natif et Git Bash (Windows).
# ---------------------------------------------------------------------------

set -euo pipefail

# URL de base de l'API — modifiez si le port ou l'hôte diffèrent.
BASE_URL="http://localhost:5000"

# --- Health check ----------------------------------------------------------
# Vérifie que l'API et la base de données sont opérationnels.
curl -sS "${BASE_URL}/health" | jq .

# --- Create user -----------------------------------------------------------
# Crée un utilisateur de démonstration (nécessaire avant d'envoyer des logs).
curl -sS -X POST "${BASE_URL}/users" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@test.com","password":"Demo123!"}' | jq .

# --- Create log ------------------------------------------------------------
# Crée un log d'erreur simulant un problème de connexion à la base de données.
curl -sS -X POST "${BASE_URL}/logs" \
  -H "Content-Type: application/json" \
  -d '{"message":"DB connection timeout","level":"ERROR","source":"api-gateway"}' | jq .

# --- Analyze log -----------------------------------------------------------
# Analyse le log d'ID 1 via le fournisseur d'IA configuré (fake par défaut).
curl -sS -X POST "${BASE_URL}/logs/1/analyze" | jq .

# --- List logs -------------------------------------------------------------
# Liste les logs de niveau ERROR, limités à 5 résultats.
curl -sS "${BASE_URL}/logs?level=ERROR&limit=5" | jq .

# --- List analyses ---------------------------------------------------------
# Liste toutes les analyses de logs précédemment effectuées.
curl -sS "${BASE_URL}/analyses" | jq .
