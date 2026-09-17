#!/bin/bash
# ---------------------------------------------------------------------------
# demo-commands.sh
# Commandes de démonstration pré-testées pour le Demo Day — Music Hall
# Compatible Linux natif et Git Bash (Windows).
# Usage: ./demo-commands.sh
# ---------------------------------------------------------------------------
set -euo pipefail

# URL de base de l'API — modifiez si le port ou l'hôte diffèrent.
BASE_URL="http://localhost:5000"

echo "=== 1. Health check — Vérifie que l'API et la base de données sont opérationnelles ==="
curl -sS "${BASE_URL}/health" | jq .
echo ""

echo "=== 2. Authentification — Récupère un token JWT pour les endpoints protégés ==="
TOKEN=$(curl -sS -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')
echo "Token reçu (premiers 20 caractères): ${TOKEN:0:20}..."
echo ""

echo "=== 3. Créer un utilisateur de démonstration (nécessaire avant d'envoyer des logs) ==="
curl -sS -X POST "${BASE_URL}/users" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{"username":"demo","email":"demo@test.com","password":"Demo123!"}' | jq .
echo ""

echo "=== 4. Créer un log — Erreur simulant un problème de connexion à la base de données ==="
curl -sS -X POST "${BASE_URL}/logs" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{"message":"DB connection timeout","level":"ERROR","source":"api-gateway"}' | jq .
echo ""

echo "=== 5. Analyser le log d'ID 1 via le fournisseur d'IA configuré (fake par défaut) ==="
curl -sS -X POST "${BASE_URL}/logs/1/analyze" \
  -H "Authorization: Bearer ${TOKEN}" | jq .
echo ""

echo "=== 6. Lister les logs de niveau ERROR, limités à 5 résultats ==="
curl -sS "${BASE_URL}/logs?level=ERROR&limit=5" \
  -H "Authorization: Bearer ${TOKEN}" | jq .
echo ""

echo "=== 7. Lister les alertes haute sévérité ==="
curl -sS "${BASE_URL}/alerts" \
  -H "Authorization: Bearer ${TOKEN}" | jq .
echo ""

echo "=== 8. Lister toutes les analyses de logs effectuées ==="
curl -sS "${BASE_URL}/analyses" \
  -H "Authorization: Bearer ${TOKEN}" | jq .
echo ""

echo "=== 9. Exporter les logs en CSV ==="
curl -sS "${BASE_URL}/export/logs?format=csv" \
  -H "Authorization: Bearer ${TOKEN}"
echo ""

echo "=== Démo terminée ==="