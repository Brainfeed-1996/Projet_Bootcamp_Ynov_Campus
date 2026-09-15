# Guide d'Intégration (Onboarding) — Log Sentinel API

Bienvenue dans l'équipe ! Ce guide te permettra de devenir productif rapidement sur le projet Log Sentinel API.

---

## 1. Prérequis Système

### Outils Obligatoires

| Outil | Version Minimale | Installation |
|-------|------------------|--------------|
| Git | 2.40+ | `winget install Git.Git` / `apt install git` |
| Python | 3.11+ | `winget install Python.Python.3.11` / `apt install python3.11` |
| Docker Desktop | 4.25+ | https://docker.com/products/docker-desktop |
| Docker Compose | v2.20+ | Inclus dans Docker Desktop |
| VS Code | 1.85+ | https://code.visualstudio.com/ |
| Make | 4.3+ | `winget install GnuWin32.Make` / `apt install make` |

### Extensions VS Code Recommandées

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.pylance",
    "ms-python.black-formatter",
    "charliermarsh.ruff",
    "ms-azuretools.vscode-docker",
    "github.vscode-pull-request-github",
    "redhat.vscode-yaml",
    "ms-vscode.makefile-tools"
  ]
}
```

Installer via : `Extentions (Ctrl+Shift+X)` → Rechercher `@recommended` → Installer tout.

---

## 2. Clonage et Configuration Initiale

```bash
# 1. Cloner le dépôt
git clone https://github.com/<org>/Log-Sentinel-API.git
cd Log-Sentinel-API

# 2. Configurer Git (une seule fois)
git config user.name "Ton Nom"
git config user.email "ton@email.com"
git config pull.rebase true
git config push.autoSetupRemote true

# 3. Vérifier l'état
git status
git log --oneline -5
```

### Configuration SSH (Recommandée)

```bash
# Générer une clé SSH si absent
ssh-keygen -t ed25519 -C "ton@email.com"

# Ajouter à l'agent SSH
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copier la clé publique
cat ~/.ssh/id_ed25519.pub
# → Coller dans GitHub/GitLab : Settings → SSH Keys
```

---

## 3. Premier Démarrage (Development)

### Option A : Docker Compose (Recommandé)

```bash
# 1. Initialiser les secrets Docker (génère ./secrets/*.txt)
./scripts/init-docker-secrets.sh

# 2. Lancer la stack complète
docker compose up --build -d

# 3. Vérifier les services
docker compose ps
# Attendu : web (healthy), db (healthy)

# 4. Test health check
curl http://localhost:5000/health
# {"status":"ok","database":"up"}

# 5. Accéder à Swagger UI
# http://localhost:5000/docs
```

### Option B : Local Python (Sans Docker)

```bash
# 1. Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows PowerShell

# 2. Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# 3. Variables d'environnement pour tests locaux
export TESTING=1
export LLM_PROVIDER=fake
export SECRET_KEY="dev-secret-key-change-me"

# 4. Lancer l'API
uvicorn app:app --host 0.0.0.0 --port 5000 --reload

# 5. Dans un autre terminal : tester
curl http://localhost:5000/health
```

---

## 4. Exécuter les Tests

### Suite Complète

```bash
# Tous les tests (avec coverage)
pytest -v --cov=app --cov-report=term-missing

# Tests rapides (sans coverage)
pytest -v -x

# Tests par module
pytest tests/test_logs.py -v
pytest tests/test_users.py -v
pytest tests/test_analyses.py -v
pytest tests/test_security.py -v
pytest tests/test_providers.py -v
```

### Tests de Performance

```bash
pytest tests/test_performance.py -v --benchmark-only
```

### Tests en Mode CI (Simule GitHub Actions)

```bash
# Linting
ruff check .

# Type checking
mypy app.py

# Security scan
bandit -r app.py -f json -o bandit-report.json

# Dependency audit
pip-audit -r requirements.txt
```

---

## 5. Structure du Projet

```
Log-Sentinel-API/
├── app.py                    # Application FastAPI principale
├── compose.yaml              # Docker Compose (dev)
├── docker-compose.production.yml  # Production overrides
├── docker-compose.vault.yml       # Vault integration
├── Dockerfile                # Image production (non-root, hardened)
├── requirements.txt          # Dépendances Python
├── .env.production.example   # Template variables prod
├── .gitignore                # Ignore .env, secrets, __pycache__, etc.
├── scripts/
│   ├── init-docker-secrets.sh    # Génère secrets Docker dev
│   └── vault-init.sh             # Initialise Vault
├── config/
│   └── vault.hcl                 # Config Vault
├── providers/
│   ├── base.py              # Interface abstraite LLM
│   ├── openai_provider.py   # OpenAI API
│   ├── ollama_provider.py   # Ollama local
│   └── fake_provider.py     # Deterministic pour tests
├── schemas/
│   └── analysis.py          # Schéma Pydantic AnalysisResult
├── tests/
│   ├── conftest.py          # Fixtures pytest partagées
│   ├── test_auth.py         # Auth / JWT
│   ├── test_users.py        # CRUD Users
│   ├── test_logs.py         # CRUD Logs + bulk/CSV
│   ├── test_analyses.py     # Analyses endpoints
│   ├── test_providers.py    # LLM providers
│   ├── test_security.py     # Pen tests (SQLi, XSS, etc.)
│   ├── test_rate_limit.py   # Rate limiting
│   ├── test_validation.py   # Validation Pydantic
│   └── test_bulk.py         # Bulk ingestion
└── data/
    └── sample_logs.csv      # Exemple pour ingest-csv
```

---

## 6. Workflow de Développement

### Créer une Feature Branch

```bash
# 1. Partir de main à jour
git checkout main
git pull origin main

# 2. Créer la branche (convention : type/description-courte)
git checkout -b feat/add-export-endpoint
# ou
git checkout -b fix/rate-limit-bypass
# ou
git checkout -b docs/update-api-reference
```

### Convention de Commits (Conventional Commits)

```bash
# Format : <type>(<scope>): <description>
# Types : feat, fix, docs, test, refactor, chore, perf, security

git add .
git commit -m "feat(logs): add CSV export endpoint"
git commit -m "fix(auth): prevent JWT replay attack"
git commit -m "docs: update API reference with bulk endpoint"
git commit -m "test: add bulk ingestion edge cases"
git commit -m "refactor(providers): extract base interface"
git commit -m "chore: update dependencies"
git commit -m "perf(db): add connection pooling"
git commit -m "security: add CSP header middleware"
```

### Pull Request

```bash
# 1. Push la branche
git push origin feat/add-export-endpoint

# 2. Créer PR sur GitHub/GitLab
#    - Titre : feat(logs): add CSV export endpoint
#    - Description : What, Why, How
#    - Labels : feature / bugfix / docs / security
#    - Assignee : toi
#    - Reviewers : 1+ membres de l'équipe

# 3. Checks obligatoires (GitHub Actions)
#    - Tests passent
#    - Linting (ruff) passe
#    - Type checking (mypy) passe
#    - Security scan (Trivy, Bandit) passe
#    - Build Docker réussit
```

### Revue de Code (Code Review)

**En tant qu'auteur :**
- PR petite et focalisée (< 400 lignes modifiées)
- Description claire du changement
- Tests ajoutés/mis à jour
- Pas de secrets dans le diff
- Self-review avant de demander review

**En tant que reviewer :**
- Vérifier : logique, sécurité, tests, performance, lisibilité
- Commenter avec `Request Changes` / `Approve` / `Comment`
- Suggérer des améliorations constructives
- Valider que les checks CI passent

---

## 7. Debugging Courant

### Logs Application

```bash
# Docker
docker compose logs -f web
docker compose logs -f web --tail=100

# Local
# Les logs vont sur stdout (configuré dans app.py)
```

### Debug Interactive (VS Code)

1. Ouvrir `app.py`
2. Ajouter un breakpoint (F9)
3. `Run and Debug` (Ctrl+Shift+D) → `Python: FastAPI`
4. Lancer : `uvicorn app:app --port 5000`
5. Appeler l'endpoint → VS Code s'arrête au breakpoint

### Debug avec `curl` / `httpie`

```bash
# httpie (plus lisible que curl)
pip install httpie

# GET
http GET localhost:5000/health
http GET localhost:5000/logs level==ERROR limit==10

# POST JSON
http POST localhost:5000/logs message="Test" level=ERROR source=api

# POST multipart (CSV)
http -f POST localhost:5000/logs/ingest-csv file@data/sample_logs.csv

# Avec headers
http POST localhost:5000/users username=test email=test@test.com password=Secret123
```

### Inspecter la Base de Données

```bash
# Via Docker (PostgreSQL)
docker compose exec db psql -U appuser -d music_hall

# Commandes SQL utiles
\dt                    # Lister les tables
\d users               # Schéma table users
SELECT * FROM users;   # Voir les users
SELECT * FROM logs ORDER BY created_at DESC LIMIT 10;
SELECT * FROM analyses ORDER BY created_at DESC LIMIT 10;

# Via SQLite (tests locaux TESTING=1)
sqlite3 test.sqlite
.tables
.schema users
SELECT * FROM logs;
```

### Problèmes Fréquents et Solutions

| Problème | Diagnostic | Solution |
|----------|------------|----------|
| `port 5000 already in use` | `lsof -i :5000` | `docker compose down` ou changer port dans `compose.yaml` |
| `/health` → `database: down` | `docker compose logs db` | Attendre healthcheck, vérifier secrets |
| `ModuleNotFoundError` | `pip list` | `pip install -r requirements.txt` |
| `pytest` → `DATABASE_URL` error | `echo $TESTING` | `export TESTING=1` |
| `401 Unauthorized` | Token JWT manquant | Vérifier header `Authorization: Bearer <token>` |
| `502 Bad Gateway` sur analyze | LLM provider down | `export LLM_PROVIDER=fake` |
| Trivy CVE HIGH | `trivy image log-sentinel:latest` | `docker pull python:3.11-slim` + rebuild |

---

## 8. Architecture Clés à Comprendre

### Fournisseurs LLM (Pluggable)

```python
# Dans app.py - get_llm_provider()
# Ordre de fallback : OpenAI → Ollama → Fake
# Variable d'env : LLM_PROVIDER=fake|openai|ollama
```

### Validation des Entrées (Pydantic)

```python
# Tous les modèles dans app.py : UserCreate, LogCreate, etc.
# Validation automatique via FastAPI → 422 si invalide
# Niveaux acceptés : DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Sécurité Conteneur

```dockerfile
# Dockerfile points clés :
USER appuser              # Non-root (UID 1000)
read_only: true           # FS read-only
tmpfs: [/tmp]             # /tmp en mémoire
cap_drop: [ALL]           # Aucune capability
no-new-privileges: true   # Empêche privilege escalation
```

### Gestion des Secrets

```bash
# Dev : ./secrets/*.txt montés via Docker Secrets
# Prod : Vault (AppRole) → secrets injectés au runtime
# JAMAIS dans .env, Dockerfile, ou Git
```

---

## 9. Ressources Utiles

### Documentation Interne

- `README.md` — Vue d'ensemble, démarrage rapide, API reference
- `SECURITY_GUIDE.md` — Modèle de menaces, headers, audit, réponse incidents
- `DEMO_DAY.md` — Script démo 6 min, plan de secours
- `CI_GUIDE.md` — Pipeline GitHub Actions, quality gates
- `QUICKREF.md` — Commandes rapides, endpoints, variables d'env
- `PITCH.md` — Pitch produit, différenciateurs
- `GUIDE_SECRETS.md` — Gestion secrets Docker/Vault
- `security_audit.md` — Rapport d'audit de sécurité

### Documentation Externe

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pydantic v2](https://docs.pydantic.dev/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/)
- [Docker Compose Spec](https://docs.docker.com/compose/compose-file/)
- [HashiCorp Vault](https://developer.hashicorp.com/vault/docs)
- [Trivy Scanner](https://aquasecurity.github.io/trivy/)
- [Conventional Commits](https://www.conventionalcommits.org/)

### Commandes de Référence Rapide

```bash
# Démarrage complet
make up          # ou docker compose up --build -d

# Tests
make test        # ou pytest -v

# Linting
make lint        # ou ruff check .

# Type check
make typecheck   # ou mypy app.py

# Security scan
make security    # ou bandit -r app.py

# Build Docker
make build       # ou docker compose build

# Nettoyage complet
make clean       # ou docker compose down -v && rm -rf secrets/
```

*(Voir `Makefile` s'il existe, sinon utiliser les commandes directes)*

---

## 10. Premiers Pas Suggérés (Semaine 1)

| Jour | Objectif | Livrable |
|------|----------|----------|
| 1 | Setup env, cloner, premier `docker compose up` | API répond sur `/health` |
| 2 | Explorer Swagger UI, tester tous les endpoints | Comprendre le flux logs → analyse |
| 3 | Lire `app.py` + `providers/` + `schemas/` | Expliquer l'architecture à un pair |
| 4 | Exécuter tous les tests, comprendre `conftest.py` | Tests verts localement |
| 5 | Faire une petite PR (ex: typo doc, test manquant) | PR mergée sur `main` |
| 6 | Review PR d'un collègue | Commentaires constructifs |
| 7 | Lire `SECURITY_GUIDE.md` + `DEMO_DAY.md` | Présenter le threat model |

---

## 11. Contacts et Support

- **Tech Lead** : @olivier-robert-duboille (GitHub)
- **Canal Slack/Discord** : #log-sentinel-dev
- **Issues** : GitHub Issues pour bugs/features
- **Documentation** : Wiki du repo / `/docs` endpoint

---

## 12. Checklist de Validation Onboarding

- [ ] Environnement local fonctionnel (Docker + Python)
- [ ] `docker compose up` → `/health` OK
- [ ] `pytest -v` → 16+ tests passed
- [ ] Swagger UI accessible sur `/docs`
- [ ] Peut créer un log, l'analyser, lister les résultats
- [ ] Comprend la structure du projet et le flux de données
- [ ] A fait au moins 1 PR (même petite)
- [ ] A review 1 PR d'un collègue
- [ ] Connaît les commandes de debug de base
- [ ] A lu `SECURITY_GUIDE.md` (threat model, headers)
- [ ] Sait où trouver les secrets (Vault/Docker Secrets)
- [ ] Comprend le fallback LLM (fake provider)

---

*Bienvenue dans l'équipe ! 🚀 N'hésite pas à poser des questions — on a tous commencé quelque part.*