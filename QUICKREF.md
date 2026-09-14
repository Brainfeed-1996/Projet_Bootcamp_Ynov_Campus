# Guide de R√©f√©rence Rapide

## Commandes Utiles

### D√©veloppement
```bash
# Installer les d√©pendances
pip install -r requirements.txt

# Lancer l'application en mode d√©veloppement
python app.py

# Lancer les tests
pytest tests/ -v

# Lancer les tests avec couverture
pytest tests/ --cov=app --cov-report=term-missing
```

### Docker
```bash
# D√©marrer l'environnement
docker compose up --build -d

# Voir les logs
docker compose logs -f

# Arr√™ter l'environnement
docker compose down

# Supprimer les volumes (ATTENTION: perd les donn√©es)
docker compose down -v
```

### Tests
```bash
# Tests unitaires
pytest tests/test_schemas.py -v

# Tests d'int√©gration
pytest tests/test_integration.py -v

# Tests de s√©curit√©
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

| M√©thode | Endpoint | Description | R√¥le requis |
|---------|----------|-------------|-------------|
| POST | /auth/login | Authentification | Aucun |
| GET | /health | Sant√© de l'API | Aucun |
| POST | /users | Cr√©er un utilisateur | admin |
| GET | /users/{id} | Lire un utilisateur | reader/writer/admin |
| DELETE | /users/{id} | Supprimer un utilisateur | admin |
| GET | /logs | Lister les logs | reader/writer/admin |
| POST | /logs | Cr√©er un log | writer/admin |
| POST | /logs/bulk | Ingestion bulk | writer/admin |
| POST | /logs/ingest-csv | Ingestion CSV | writer/admin |
| POST | /logs/{id}/analyser | Analyser un log | writer/admin |
| GET | /analyses | Lister les analyses | reader/writer/admin |
| POST | /analyses | Cr√©er une analyse | writer/admin |
| GET | /alerts | Alertes haute s√©v√©rit√© | reader/writer/admin |

## Configuration

### Variables d'environnement requises

| Variable | Description | D√©faut |
|----------|-------------|--------|
| SECRET_KEY | Cl√© secr√®te JWT | default-secret-key-change-me |
| DATABASE_URL | URL de la base de donn√©es | - |
| DB_USER | Utilisateur DB | - |
| DB_PASSWORD | Mot de passe DB | - |
| LLM_PROVIDER | Fournisseur LLM (openai/ollama/fake) | - |
| OPENAI_API_KEY | Cl√© API OpenAI | - |
| OLLAMA_BASE_URL | URL Ollama | http://localhost:11434 |

## R√©solution de Probl√®mes

### Erreur 401 / Token expir√©
1. V√©rifiez que vous passez un token JWT valide
2. Le token expire apr√®s 30 minutes par d√©faut
3. Reconnectez-vous pour obtenir un nouveau token

### Erreur 422 / Validation
1. V√©rifiez le format des donn√©es envoy√©es
2. Consultez le sch√©ma OpenAPI (/openapi.json)
3. V√©rifiez les contraintes de longueur

### Erreur 409 / Conflit
L'entr√©e existe d√©j√† (nom d'utilisateur ou email duplicate)

### Erreur 500 / Erreur interne
1. Consultez les logs serveur
2. V√©rifiez la connexion √† la base de donn√©es
3. V√©rifiez la configuration des variables d'environnement
## Variables d'Environnement

| Variable | Description | Exemple |
|----------|-------------|--------|
| SECRET_KEY | ClÈ secrËte JWT | 64 caractËres hex |
| DATABASE_URL | URL PostgreSQL | postgresql://user:pass@host/db |
| LLM_PROVIDER | Fournisseur LLM | openai, ollama, fake |

## ProblËmes Courants

### Erreur de connexion ‡ la base
1. VÈrifier que PostgreSQL est dÈmarrÈ
2. VÈrifier les identifiants dans .env
3. VÈrifier les pare-feu et DNS

### Erreur d'authentification
1. VÈrifier la clÈ secrËte
2. VÈrifier la validitÈ du token
3. VÈrifier les rÙles de l'utilisateur

## Rate Limiting

L'API applique les limites suivantes :
- Authentification : 10/minute
- CrÈation de logs : 50/minute
- Analyse IA : 30/minute
- Lecture : 100/minute

Les rÈponses incluent les headers :
- X-RateLimit-Limit
- X-RateLimit-Remaining
- X-RateLimit-Reset

## Export des DonnÈes

L'API permet d'exporter les logs dans diffÈrents formats :
- JSON (dÈfaut)
- CSV
- Excel (‡ venir)

Endpoints :
- `GET /export/logs` : Exporter les logs
- `GET /export/analyses` : Exporter les analyses
