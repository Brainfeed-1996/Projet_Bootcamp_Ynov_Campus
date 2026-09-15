# Log Sentinel API

API **FastAPI** d'ingestion et d'analyse de logs sécurisée, conçue pour un cours **DevSecOps** (Ynov — Défensive).

**Version** : `v1.1.0`  
**Stack** : Python 3.11+, FastAPI, PostgreSQL, Docker, Docker Compose, Trivy, Vault (optionnel).

---

## Table des matières

1. [Prérequis](#prérequis)
2. [Installation](#installation)
3. [Tests automatisés sans IA réelle](#tests-automatisés-sans-ia-réelle)
4. [Démarrage rapide](#démarrage-rapide)
5. [Sécurité et secrets](#sécurité-et-secrets)
6. [Endpoints](#endpoints)
7. [CI/CD et scan](#cicd-et-scan)
8. [Démo Demo Day](#démo-demo-day)
9. [Problèmes courants et solutions](#problèmes-courants-et-solutions)
10. [Définition of Done](#définition-of-done)
11. [Support et nettoyage](#support-et-nettoyage)
12. [Architecture](#architecture)
13. [Contribuer](#contribuer)

---

## Architecture

Le projet suit une architecture en 3 couches :

```
┌─────────────────┝     ┌──────────────────┝     ┌─────────────────┝
│   Client HTTP   │────▶│   FastAPI App    │────▶│  PostgreSQL DB  │
│   (curl/docs)   │     │   (app.py)       │     │  (users/logs)   │
└─────────────────┘     └────────┬─────────┘     └─────────────────┘
                                │
                        ┌───────┴────────┝
                        │  LLM Providers │
                        │  (OpenAI/Ollama│
                        │   /Fake)       │
                        └────────────────┘
```

### Composants

- **app.py** : Application FastAPI principale avec authentification JWT
- **providers/** : Fournisseurs LLM (OpenAI, Ollama, Fake pour les tests)
- **schemas/** : Modèles Pydantic pour la validation
- **scripts/** : Scripts d'initialisation Docker et Vault
- **config/** : Configurations Vault (optionnel)
- **tests/** : Suite de tests complets

---

## Contribuer

1. Fork le dépôt
2. Créer une branche feature (`git checkout -b feature/ma-fonctionnalité`)
3. Commit les changements (`git commit -m "feat: ma fonctionnalité"`)
4. Push la branche (`git push origin feature/ma-fonctionnalité`)
5. Créer une Pull Request

### Style des commits

Utiliser [Conventional Commits](https://www.conventionalcommits.org/) :
- `feat` : Nouvelle fonctionnalité
- `fix` : Correction de bug
- `docs` : Documentation
- `test` : Tests
- `chore` : Maintenance
- `refactor` : Refactoring
- `perf` : Performance
- `security` : Sécurité

---

## Prérequis

- Python 3.11+ et `pip`
- Docker et Docker Compose (pour le conteneurisé)
- Git

Variables d'environnement locales : copiez `.env.production.example` en `.env.production` et adaptez les secrets si vous lancez la production hors Docker.

---

## Installation

### Sans Docker (développement local)

```bash
pip install -r requirements.txt
```

### Avec Docker (recommandé)

```bash
./scripts/init-docker-secrets.sh
docker compose up --build -d
```

---

## Tests automatisés sans IA réelle

```bash
pytest -v
```

La suite utilise `LLM_PROVIDER=fake` par défaut et une base SQLite en mémoire si `TESTING=1`. Aucune requête vers OpenAI, Ollama ou PostgreSQL n'est exécutée.

- 16 tests couvrent : health, utilisateurs, validation, logs, analyse avec fournisseur factice, gestion d'erreurs et endpoints analyses.
- Fournisseurs IA robustifiés : validation JSON stricte, timeouts, URL sécurisée, faux fournisseur déterministe.
- Aucun secret n'est affiché ni commité.

---

## Démarrage rapide

### 1. Initialiser les secrets Docker (développement local)

```bash
./scripts/init-docker-secrets.sh
```

### 2. Lancer l'application

```bash
docker compose up --build -d
docker compose ps
curl http://localhost:5000/health
```

### 3. Arrêter

```bash
docker compose down -v
```

---

## Sécurité et secrets

- `.env` et `.env.production` sont **ignorés** par Git et Docker.
- Les secrets sont stockés dans `./secrets/*.txt` et montés via **Docker Secrets** (`compose.yaml`, `docker-compose.production.yml`).
- Aucune valeur par défaut n'est utilisée en production.
- Production : `docker compose -f compose.yaml -f docker-compose.production.yml up --build -d`.
- Vault : `docker compose -f compose.yaml -f docker-compose.vault.yml up --build -d`.

### Clean machine

```bash
git clone <repository>
cd Log Sentinel API
./scripts/init-docker-secrets.sh
docker compose up --build -d
pytest -v
```

---

## Endpoints

Le provider LLM par défaut est `fake` (déterministe, sans réseau). Pour utiliser OpenAI ou Ollama, définissez `LLM_PROVIDER=openai` ou `LLM_PROVIDER=ollama` avec les variables d'environnement requises.

```bash
# Santé
curl http://localhost:5000/health

# Utilisateurs
curl -X POST http://localhost:5000/users -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"SuperSecret1"}'
curl http://localhost:5000/users/1
curl -X DELETE http://localhost:5000/users/1

# Logs
curl -X POST http://localhost:5000/logs -H "Content-Type: application/json" \
  -d '{"message":"Connection timeout","level":"ERROR","source":"api"}'
curl "http://localhost:5000/logs?level=ERROR&limit=10"
curl -X POST http://localhost:5000/logs/ingest-csv -F "file=@data/sample_logs.csv"

# Analyse (fake provider)
curl -X POST http://localhost:5000/logs/1/analyze
curl http://localhost:5000/analyses
```

---

## R�f�rence API Compl�te

L'API est document�e via OpenAPI/Swagger � `/docs` (interface interactive) et `/openapi.json` (sch�ma brut).

### Authentification

Toutes les routes (sauf `/health` et `/docs`) n�cessitent un token JWT dans l'en-t�te `Authorization: Bearer <token>`. Obtenir un token via `POST /auth/login` (non impl�ment� dans cette version, voir `GET /users/{id}` pour lecture seule).

### Rate Limiting

| Endpoint | Limite |
|----------|--------|
| Authentification | 10 req/min |
| Cr�ation de logs | 50 req/min |
| Analyse IA | 30 req/min |
| Lecture (GET) | 100 req/min |

Headers de r�ponse : `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.

### Utilisateurs (`/users`)

| M�thode | Endpoint | Description | Corps de requ�te | R�ponse succ�s |
|---------|----------|-------------|------------------|----------------|
| `GET` | `/users/{user_id}` | R�cup�rer un utilisateur par ID | � | `200 UserRead` |
| `POST` | `/users` | Cr�er un utilisateur | `UserCreate` | `201 UserRead` |
| `DELETE` | `/users/{user_id}` | D�sactiver un utilisateur (soft delete) | � | `200 {id, status}` |

**UserCreate** :
```json
{
  "username": "string (3-50 chars, unique)",
  "email": "string (email valide, unique, max 120)",
  "password": "string (min 8 chars)"
}
```

**UserRead** :
```json
{
  "id": "integer",
  "username": "string",
  "email": "string",
  "is_active": "boolean"
}
```

**Erreurs** :
- `400` : ID invalide (? 0)
- `404` : Utilisateur introuvable ou inactif
- `409` : Username ou email d�j� existant
- `422` : Validation �chou�e (champs manquants, format invalide)

### Logs (`/logs`)

| M�thode | Endpoint | Description | Param�tres / Corps | R�ponse succ�s |
|---------|----------|-------------|-------------------|----------------|
| `GET` | `/logs` | Lister les logs avec filtres | `level?`, `source?`, `limit? (1-1000, d�faut 100)` | `200 [LogRead]` |
| `POST` | `/logs` | Cr�er un log | `LogCreate` | `201 LogRead` |
| `GET` | `/logs/{log_id}` | R�cup�rer un log par ID | � | `200 LogRead` |
| `POST` | `/logs/bulk` | Ingestion bulk JSON | `[LogCreate, ...]` (max 10000) | `200 BulkResult` |
| `POST` | `/logs/ingest-csv` | Ingestion CSV (multipart) | Fichier `.csv` avec colonnes `message`, `level?`, `source?` | `200 BulkResult` |
| `POST` | `/logs/{log_id}/analyze` | Analyser un log via LLM | � | `201 {id, log_id, result}` |

**LogCreate** :
```json
{
  "message": "string (1-4096 chars, requis)",
  "level": "string (DEBUG/INFO/WARNING/ERROR/CRITICAL, d�faut INFO)",
  "source": "string (1-100 chars, d�faut 'unknown')"
}
```

**LogRead** :
```json
{
  "id": "integer",
  "level": "string",
  "message": "string",
  "source": "string | null",
  "created_at": "ISO8601 datetime | null"
}
```

**BulkResult** :
```json
{
  "ingested": "integer",
  "rejected": "integer",
  "errors": ["string", ...]
}
```

**Analyse Result** :
```json
{
  "id": "integer",
  "log_id": "integer",
  "result": {
    "severity": "LOW|MEDIUM|HIGH|CRITICAL",
    "category": "string (ex: AUTH, NETWORK, SYSTEM)",
    "summary": "string",
    "recommendations": ["string", ...],
    "provider": "fake|openai|ollama"
  }
}
```

**Erreurs** :
- `400` : ID invalide, limit hors bornes, level invalide, source vide
- `404` : Log introuvable
- `413` : Corps trop volumineux (> 10 MB) ou fichier CSV trop gros
- `422` : Validation �chou�e, CSV invalide (colonne `message` requise)
- `502` : Provider LLM indisponible
- `503` : Base de donn�es indisponible

### Analyses (`/analyses`)

| M�thode | Endpoint | Description | Corps de requ�te | R�ponse succ�s |
|---------|----------|-------------|------------------|----------------|
| `GET` | `/analyses` | Lister les analyses | `limit? (1-1000, d�faut 50)` | `200 [AnalyseRead]` |
| `POST` | `/analyses` | Cr�er une analyse manuelle | `{type, input_data?, result?}` | `201 AnalyseRead` |

**AnalyseRead** :
```json
{
  "id": "integer",
  "type": "string",
  "input_data": "string | null",
  "result": "string | null",
  "created_at": "ISO8601 datetime | null"
}
```

### Sant� et Monitoring (`/health`, `/metrics`)

| M�thode | Endpoint | Description | R�ponse succ�s |
|---------|----------|-------------|----------------|
| `GET` | `/health` | V�rifier sant� API + DB | `200 {status: "ok", database: "up"}` ou `503 {status: "error", database: "down"}` |
| `GET` | `/metrics` | M�triques Prometheus (si configur�) | Format Prometheus text |

### Codes d'erreur globaux

| Code | Signification |
|------|---------------|
| `200` | Succ�s (GET, PUT, DELETE) |
| `201` | Cr�� (POST) |
| `400` | Requ�te invalide (param�tres, validation m�tier) |
| `401` | Non authentifi� (token manquant/invalide) |
| `403` | Interdit (CSRF, permissions insuffisantes) |
| `404` | Ressource introuvable |
| `409` | Conflit (doublon unique) |
| `413` | Payload trop volumineux |
| `422` | Erreur de validation Pydantic |
| `500` | Erreur interne serveur |
| `502` | Provider LLM indisponible |
| `503` | Service indisponible (DB down) |

### Exemples complets

**Cr�er un utilisateur** :
```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"bob","email":"bob@example.com","password":"SecurePass123"}'
```

**Cr�er un log** :
```bash
curl -X POST http://localhost:5000/logs \
  -H "Content-Type: application/json" \
  -d '{"message":"Database connection pool exhausted","level":"CRITICAL","source":"postgres"}'
```

**Filtrer les logs** :
```bash
curl "http://localhost:5000/logs?level=ERROR&source=api&limit=20"
```

**Ingestion bulk** :
```bash
curl -X POST http://localhost:5000/logs/bulk \
  -H "Content-Type: application/json" \
  -d '[{"message":"Error 1","level":"ERROR"},{"message":"Warning 1","level":"WARNING"}]'
```

**Ingestion CSV** :
```bash
curl -X POST http://localhost:5000/logs/ingest-csv \
  -F "file=@logs.csv"
```

**Analyser un log** :
```bash
curl -X POST http://localhost:5000/logs/1/analyze
```

**Lister les analyses** :
```bash
curl "http://localhost:5000/analyses?limit=10"
```

---

## CI/CD et scan

- `.github/workflows/ci.yml` : tests, build Docker, Trivy, Snyk.
- `Dockerfile` : image non-root `appuser` (UID 1000), build reproductible.
- `compose.yaml` : secrets Docker, `read_only`, tmpfs, limites et `cap_drop ALL` en production.
- Le scan Trivy est exécuté dans le pipeline CI, pas dans l'image de build.

---

## Démo Demo Day

Consultez `DEMO_DAY.md` pour le support de démonstration :

- Durée : **6 minutes** de démo + Q&A.
- Répartition du temps de parole : **50/50** entre Presenter A et Presenter B.
- Plan minute par minute avec commandes et résultats attendus.
- Plan de secours sans IA et sans Docker.

---

## Définition of Done

- [x] Projet repart sur une machine propre avec `git clone`, `./scripts/init-docker-secrets.sh`, `docker compose up`.
- [x] Tests automatisés passent sans accès à une vraie IA ni à PostgreSQL.
- [x] Jeu de démonstration tient en six minutes et la parole est répartie à 50/50.
- [x] Code versionné et tagué `v1.1.0` (depuis `v1.0.0`).
- [x] Documentation finale et support Demo Day fournis.
- [x] Secrets exclus de Git et de l'image Docker.
- [x] Fournisseurs IA validés sans réseau et avec erreurs explicites.

---

## Problèmes courants et solutions

| Problème | Cause probable | Solution |
|----------|---------------|----------|
| `port 5000 already in use` | Un autre service utilise le port | `docker compose down` ou changer le port dans `compose.yaml` (ex: `5001:5000`) |
| `/health` retourne `503` — `database: down` | PostgreSQL pas encore prêt ou secrets manquants | Vérifier `docker compose logs db` ; attendre le healthcheck ; relancer `./scripts/init-docker-secrets.sh` |
| `ModuleNotFoundError` | Dépendances non installées | `pip install -r requirements.txt` (hors Docker) ou `docker compose up --build` |
| `/logs/1/analyze` retourne `502` | LLM externe (OpenAI/Ollama) injoignable | Vérifier `LLM_PROVIDER` : mettre `fake` pour la démo offline. Le fallback est automatique. |
| `pytest` échoue avec `RuntimeError: DATABASE_URL` | `TESTING` non défini en local | `TESTING=1 pytest -v` active SQLite en mémoire |
| `.env` missing / secrets introuvables | Fichier `.env` absent ou non initialisé | `cp .env.production.example .env.production` puis adapter les valeurs |
| Trivy trouve des CVE HIGH/CRITICAL | Image de base vulnérable | `docker pull python:3.11-slim` puis rebuild ; vérifier `.trivyignore` pour les exceptions justifiées |
| Tests échouent sur une machine propre | Démarrage incomplet | `git clone`, `./scripts/init-docker-secrets.sh`, `docker compose up --build -d`, puis `pytest -v` |
| JSON invalide dans les requêtes curl | Guillemets ou apostrophes mal échappés | Utiliser les commandes du `demo-commands.sh` ou du fichier `DEMO_DAY.md` |
| `docker compose` non trouvé | Docker non installé ou non démarré | Installer Docker Desktop ; vérifier `docker --version` et `docker compose version` |

---

## Support et nettoyage

```bash
# Logs Docker
docker compose logs -f web
docker compose logs -f db

# Réinitialiser la base SQLite de test
rm -f test.sqlite test.sqlite-shm test.sqlite-wal
pytest -v
```

## Rate Limiting

L'API utilise un rate limiting pour prot�ger contre les abus :
- Authentification : 10 tentatives/minute
- Cr�ation de logs : 50/minute
- Analyse IA : 30/minute

## Changelog

### v1.1.0 (2025-09)
- Ajout du rate limiting
- Am�lioration de la s�curit� (headers, validation)
- Ajout des tests de performance
- Documentation compl�te

## Sch�ma de Base de Donn�es

### Table users
- id: Identifiant unique
- username: Nom d'utilisateur (unique)
- email: Adresse email (unique)
- password_hash: Mot de passe hach�
- role: R�le (admin/writer/reader)
- is_active: Compte actif
- created_at: Date de cr�ation

### Table logs
- id: Identifiant unique
- occurred_at: Horodatage de l'�v�nement
- level: Niveau (DEBUG/INFO/WARNING/ERROR/CRITICAL)
- message: Contenu du log
- source: Source du log
- log_metadata: M�tadonn�es JSON
- created_at: Date d'ingestion

## Contribuer

### Avant de committer
1. Ex�cuter les tests : `pytest tests/ -v`
2. V�rifier le linting : `ruff check .`
3. V�rifier les types : `mypy app.py`
4. Ne jamais commit de secrets

### Style des commits
- `feat` : Nouvelle fonctionnalit�
- `fix` : Correction de bug
- `docs` : Documentation
- `test` : Tests
- `refactor` : Refactoring
- `chore` : Maintenance

## Versioning

L'API utilise le versioning par URL :
- `/api/v1/` : Version actuelle
- `/api/v2/` : Version future (d�veloppement)

La version est indiqu�e dans le sch�ma OpenAPI.

## Observabilit�

### Stack
- **Logs** : Loki + Grafana
- **Metrics** : Prometheus + Grafana
- **Tracing** : Jaeger
- **Alerting** : Alertmanager

### Dashboard
- Disponibile � http://grafana:3000
- Identifiants : admin/admin
