# Guide de RÃ©fÃ©rence Rapide

## Commandes Utiles

### DÃ©veloppement
```bash
# Installer les dÃ©pendances
pip install -r requirements.txt

# Lancer l'application en mode dÃ©veloppement
python app.py

# Lancer les tests
pytest tests/ -v

# Lancer les tests avec couverture
pytest tests/ --cov=app --cov-report=term-missing
```

### Docker
```bash
# DÃ©marrer l'environnement
docker compose up --build -d

# Voir les logs
docker compose logs -f

# ArrÃªter l'environnement
docker compose down

# Supprimer les volumes (ATTENTION: perd les donnÃ©es)
docker compose down -v
```

### Tests
```bash
# Tests unitaires
pytest tests/test_schemas.py -v

# Tests d'intÃ©gration
pytest tests/test_integration.py -v

# Tests de sÃ©curitÃ©
pytest tests/test_security.py -v

# Tests de performance
pytest tests/test_performance.py -v

# Tous les tests
pytest tests/ -v --tb=short
```

### Debug
```python
# Dans debug_csv.py
python debug_csv.py
```

## Endpoints Rapides

| MÃ©thode | Endpoint | Description | RÃ´le requis |
|---------|----------|-------------|-------------|
| POST | /auth/login | Authentification | Aucun |
| GET | /health | SantÃ© de l'API | Aucun |
| POST | /users | CrÃ©er un utilisateur | admin |
| GET | /users/{id} | Lire un utilisateur | reader/writer/admin |
| DELETE | /users/{id} | Supprimer un utilisateur | admin |
| GET | /logs | Lister les logs | reader/writer/admin |
| POST | /logs | CrÃ©er un log | writer/admin |
| POST | /logs/bulk | Ingestion bulk | writer/admin |
| POST | /logs/ingest-csv | Ingestion CSV | writer/admin |
| POST | /logs/{id}/analyser | Analyser un log | writer/admin |
| GET | /analyses | Lister les analyses | reader/writer/admin |
| POST | /analyses | CrÃ©er une analyse | writer/admin |
| GET | /alerts | Alertes haute sÃ©vÃ©ritÃ© | reader/writer/admin |

## Configuration

### Variables d'environnement requises

| Variable | Description | DÃ©faut |
|----------|-------------|--------|
| SECRET_KEY | ClÃ© secrÃ¨te JWT | default-secret-key-change-me |
| DATABASE_URL | URL de la base de donnÃ©es | - |
| DB_USER | Utilisateur DB | - |
| DB_PASSWORD | Mot de passe DB | - |
| LLM_PROVIDER | Fournisseur LLM (openai/ollama/fake) | - |
| OPENAI_API_KEY | ClÃ© API OpenAI | - |
| OLLAMA_BASE_URL | URL Ollama | http://localhost:11434 |

## RÃ©solution de ProblÃ¨mes

### Erreur 401 / Token expirÃ©
1. VÃ©rifiez que vous passez un token JWT valide
2. Le token expire aprÃ¨s 30 minutes par dÃ©faut
3. Reconnectez-vous pour obtenir un nouveau token

### Erreur 422 / Validation
1. VÃ©rifiez le format des donnÃ©es envoyÃ©es
2. Consultez le schÃ©ma OpenAPI (/openapi.json)
3. VÃ©rifiez les contraintes de longueur

### Erreur 409 / Conflit
L'entrÃ©e existe dÃ©jÃ  (nom d'utilisateur ou email duplicate)

### Erreur 500 / Erreur interne
1. Consultez les logs serveur
2. VÃ©rifiez la connexion Ã  la base de donnÃ©es
3. VÃ©rifiez la configuration des variables d'environnement
## Variables d'Environnement

| Variable | Description | Exemple |
|----------|-------------|--------|
| SECRET_KEY | Clé secrète JWT | 64 caractères hex |
| DATABASE_URL | URL PostgreSQL | postgresql://user:pass@host/db |
| LLM_PROVIDER | Fournisseur LLM | openai, ollama, fake |

## Problèmes Courants

### Erreur de connexion à la base
1. Vérifier que PostgreSQL est démarré
2. Vérifier les identifiants dans .env
3. Vérifier les pare-feu et DNS

### Erreur d'authentification
1. Vérifier la clé secrète
2. Vérifier la validité du token
3. Vérifier les rôles de l'utilisateur

## Rate Limiting

L'API applique les limites suivantes :
- Authentification : 10/minute
- Création de logs : 50/minute
- Analyse IA : 30/minute
- Lecture : 100/minute

Les réponses incluent les headers :
- X-RateLimit-Limit
- X-RateLimit-Remaining
- X-RateLimit-Reset

## Export des Données

L'API permet d'exporter les logs dans différents formats :
- JSON (défaut)
- CSV
- Excel (à venir)

Endpoints :
- `GET /export/logs` : Exporter les logs
- `GET /export/analyses` : Exporter les analyses
