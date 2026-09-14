# Guide de Référence Rapide

## Commandes Utiles

### Développement
```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application en mode développement
python app.py

# Lancer les tests
pytest tests/ -v

# Lancer les tests avec couverture
pytest tests/ --cov=app --cov-report=term-missing
```

### Docker
```bash
# Démarrer l'environnement
docker compose up --build -d

# Voir les logs
docker compose logs -f

# Arrêter l'environnement
docker compose down

# Supprimer les volumes (ATTENTION: perd les données)
docker compose down -v
```

### Tests
```bash
# Tests unitaires
pytest tests/test_schemas.py -v

# Tests d'intégration
pytest tests/test_integration.py -v

# Tests de sécurité
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

| Méthode | Endpoint | Description | Rôle requis |
|---------|----------|-------------|-------------|
| POST | /auth/login | Authentification | Aucun |
| GET | /health | Santé de l'API | Aucun |
| POST | /users | Créer un utilisateur | admin |
| GET | /users/{id} | Lire un utilisateur | reader/writer/admin |
| DELETE | /users/{id} | Supprimer un utilisateur | admin |
| GET | /logs | Lister les logs | reader/writer/admin |
| POST | /logs | Créer un log | writer/admin |
| POST | /logs/bulk | Ingestion bulk | writer/admin |
| POST | /logs/ingest-csv | Ingestion CSV | writer/admin |
| POST | /logs/{id}/analyser | Analyser un log | writer/admin |
| GET | /analyses | Lister les analyses | reader/writer/admin |
| POST | /analyses | Créer une analyse | writer/admin |
| GET | /alerts | Alertes haute sévérité | reader/writer/admin |

## Configuration

### Variables d'environnement requises

| Variable | Description | Défaut |
|----------|-------------|--------|
| SECRET_KEY | Clé secrète JWT | default-secret-key-change-me |
| DATABASE_URL | URL de la base de données | - |
| DB_USER | Utilisateur DB | - |
| DB_PASSWORD | Mot de passe DB | - |
| LLM_PROVIDER | Fournisseur LLM (openai/ollama/fake) | - |
| OPENAI_API_KEY | Clé API OpenAI | - |
| OLLAMA_BASE_URL | URL Ollama | http://localhost:11434 |

## Résolution de Problèmes

### Erreur 401 / Token expiré
1. Vérifiez que vous passez un token JWT valide
2. Le token expire après 30 minutes par défaut
3. Reconnectez-vous pour obtenir un nouveau token

### Erreur 422 / Validation
1. Vérifiez le format des données envoyées
2. Consultez le schéma OpenAPI (/openapi.json)
3. Vérifiez les contraintes de longueur

### Erreur 409 / Conflit
L'entrée existe déjà (nom d'utilisateur ou email duplicate)

### Erreur 500 / Erreur interne
1. Consultez les logs serveur
2. Vérifiez la connexion à la base de données
3. Vérifiez la configuration des variables d'environnement
## Variables d'Environnement

| Variable | Description | Exemple |
|----------|-------------|--------|
| SECRET_KEY | Cl� secr�te JWT | 64 caract�res hex |
| DATABASE_URL | URL PostgreSQL | postgresql://user:pass@host/db |
| LLM_PROVIDER | Fournisseur LLM | openai, ollama, fake |

## Probl�mes Courants

### Erreur de connexion � la base
1. V�rifier que PostgreSQL est d�marr�
2. V�rifier les identifiants dans .env
3. V�rifier les pare-feu et DNS

### Erreur d'authentification
1. V�rifier la cl� secr�te
2. V�rifier la validit� du token
3. V�rifier les r�les de l'utilisateur
