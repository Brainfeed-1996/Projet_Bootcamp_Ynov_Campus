# API Changelog & Versioning Policy — Log Sentinel API

---

## Politique de Versioning

### Semantic Versioning (SemVer 2.0.0)

L'API suit **SemVer** : `MAJOR.MINOR.PATCH`

| Version | Quand | Exemple | Compatibilité |
|---------|-------|---------|---------------|
| **MAJOR** | Breaking changes (suppression endpoint, changement format réponse, auth) | `1.0.0` → `2.0.0` | ❌ Incompatible |
| **MINOR** | Nouvelles fonctionnalités rétrocompatibles (nouvel endpoint, champ optionnel) | `1.0.0` → `1.1.0` | ✅ Compatible |
| **PATCH** | Corrections de bugs rétrocompatibles (fix validation, perf, sécurité) | `1.0.0` → `1.0.1` | ✅ Compatible |

### Versioning par URL

```
API v1 (actuelle)  : /api/v1/  ou  / (racine)
API v2 (future)    : /api/v2/
```

- La version est indiquée dans `openapi.json` : `"version": "1.1.0"`
- Header de réponse : `X-API-Version: 1.1.0`
- Dépréciation : header `Sunset: <date>` 6 mois avant retrait

### Cycle de Vie des Versions

| Phase | Durée | Support |
|-------|-------|---------|
| **Active** | 12-18 mois | Nouvelles features, bug fixes, security patches |
| **Maintenance** | 6 mois | Security patches uniquement |
| **Deprecated** | 6 mois (avec header `Sunset`) | Aucun nouveau développement |
| **Retired** | — | Retirée, redirection 410 Gone |

### Branching Strategy (GitFlow Adapté)

```
main (production)     → Tags: v1.0.0, v1.1.0, v2.0.0
  ↑
develop (staging)     → CI continu, tests complets
  ↑
feature/*             → Une feature par branche
hotfix/*              → Correctifs urgents sur main
release/*             → Préparation release (version bump, changelog)
```

### Conventional Commits → Version Bump

| Commit Type | Version Bump | Exemple |
|-------------|--------------|---------|
| `feat:` | MINOR | `feat(logs): add bulk export` |
| `fix:` | PATCH | `fix(auth): prevent token replay` |
| `feat!:` / `BREAKING CHANGE:` | MAJOR | `feat!(auth): remove JWT, add OAuth2` |
| `docs:`, `chore:`, `refactor:`, `test:`, `style:` | Aucun (sauf si dans release branch) | — |

---

### Contrat de compatibilité

- Une version **MINOR** peut ajouter un endpoint, un champ de réponse ou une option de requête, mais ne doit pas modifier le comportement d'un contrat existant.
- Une version **MAJOR** est obligatoire pour supprimer un endpoint, renommer un champ, changer son type, durcir une règle de validation de manière incompatible ou modifier le schéma d'authentification.
- Toute modification incompatible doit être accompagnée d'un guide de migration, d'une période de dépréciation et d'un exemple de requête/réponse avant et après.
- Les endpoints marqués comme expérimentaux ou internes peuvent évoluer sans garantie de stabilité ; ils ne doivent pas être consommés comme contrat public.
- Les correctifs de sécurité peuvent être publiés en **PATCH** lorsqu'ils préservent le contrat ; un changement de sécurité incompatible relève d'une version **MAJOR**.

---

## Changelog

### [Unreleased] — Develop Branch

#### Added
- Nouvel endpoint `GET /export/logs` (JSON/CSV/Excel)
- Nouvel endpoint `GET /export/analyses`
- Support webhook pour notifications temps réel (`POST /webhooks`)
- Métriques Prometheus `/metrics` exposées par défaut
- Rate limiting granulaire par IP + utilisateur

#### Changed
- Amélioration performances bulk ingestion (batch inserts)
- Timeout LLM provider configurable via `LLM_TIMEOUT_SECONDS`
- Logs structurés JSON par défaut (Loki-ready)

#### Fixed
- Race condition sur soft-delete users (concurrent DELETE)
- Fuite potentielle d'IP dans logs d'erreur (redaction renforcée)
- Memory leak dans FakeProvider sous charge soutenue

#### Security
- Mise à jour dépendances : `cryptography>=42.0`, `pydantic>=2.8`
- CSP header renforcé (`script-src 'self' 'nonce-...'`)

---

### [1.1.0] — 2025-09-15

#### Added
- **Rate Limiting** middleware (token bucket, Redis-backed optionnel)
  - Auth: 10 req/min
  - Logs write: 50 req/min
  - Analyze: 30 req/min
  - Default: 100 req/min
- Headers rate limit : `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- **Security Headers** middleware (CSP, X-Frame-Options, X-Content-Type-Options, etc.)
- **Request Size Limit** : 10 MB max (configurable via `MAX_REQUEST_SIZE`)
- **CSRF Protection** middleware pour endpoints state-changing
- Tests de performance (`tests/test_performance.py`) avec benchmarks
- Documentation complète : API Reference, Deployment Guide, Onboarding, Runbook

#### Changed
- `SECRET_KEY` : défaut supprimé, obligatoire en production
- `LLM_PROVIDER` : fallback chain OpenAI → Ollama → Fake (au lieu de Fake seulement)
- Dockerfile : multi-stage build, non-root user (UID 1000), read-only FS, cap_drop ALL
- `docker-compose.production.yml` : resource limits, restart policies, healthchecks
- Vault integration : AppRole auth, secret rotation support

#### Fixed
- Validation `level` case-insensitive + whitelist stricte
- CSV ingestion : encoding UTF-8 strict, colonnes requises validées
- Bulk ingestion : limite 10k items, erreurs détaillées par ligne
- Health check DB : retry logic avec backoff exponentiel

#### Security
- Trivy scan intégré dans CI (bloquant sur HIGH/CRITICAL)
- Snyk scan dependencies + code (SARIF upload GitHub Security)
- Bandit + Semgrep dans pipeline
- `.trivyignore` pour exceptions justifiées (documentées)

#### Deprecated
- Endpoint `/auth/login` (non implémenté, retour 501) — sera ajouté en v1.2
- Variable `DATABASE_URL` directe (remplacée par Docker Secrets + Vault)

---

### [1.0.0] — 2025-09-01 (Demo Day Release)

#### Added - Core Features
- **Users Management**
  - `POST /users` — Création utilisateur (bcrypt hash, unicité username/email)
  - `GET /users/{id}` — Lecture utilisateur (validation ID > 0)
  - `DELETE /users/{id}` — Soft delete (`is_active=false`)
- **Logs Ingestion**
  - `POST /logs` — Création log unique (validation Pydantic)
  - `GET /logs` — Liste avec filtres `level`, `source`, `limit` (1-1000)
  - `GET /logs/{id}` — Lecture log par ID
  - `POST /logs/bulk` — Ingestion bulk JSON (max 10k items)
  - `POST /logs/ingest-csv` — Ingestion CSV multipart (colonnes: message, level?, source?)
- **Log Analysis (LLM)**
  - `POST /logs/{id}/analyze` — Analyse via provider LLM pluggable
  - Providers : OpenAI, Ollama, Fake (deterministic, offline)
  - Schéma résultat : `severity`, `category`, `summary`, `recommendations`, `provider`
- **Analyses Management**
  - `GET /analyses` — Liste analyses (limit 1-1000, défaut 50)
  - `POST /analyses` — Création analyse manuelle
- **Health & Monitoring**
  - `GET /health` — Santé API + DB (`{"status":"ok","database":"up"}`)
  - Structured logging (JSON) pour Loki

#### Added - Infrastructure
- Docker Compose stack : `web` (FastAPI), `db` (PostgreSQL 15-alpine)
- Docker Secrets pour gestion secrets (pas de secrets en image/env)
- `scripts/init-docker-secrets.sh` — Génération secrets dev
- Vault integration optionnelle (`docker-compose.vault.yml`)
- Healthchecks Docker (DB `pg_isready`, Web `/health`)
- Volumes persistants PostgreSQL

#### Added - Security
- JWT Authentication (HS256, 30min expiry) — infrastructure prête
- bcrypt password hashing (cost 12)
- Paramétrisation SQL (SQLAlchemy text() + params, pas de concaténation)
- Validation Pydantic stricte (whitelist levels, longueur max, email valide)
- Soft delete users (traçabilité)
- `.gitignore` exclut `.env`, `secrets/`, `*.sqlite`, `__pycache__`

#### Added - Testing
- 16 tests automatisés (`pytest -v`)
- `TESTING=1` → SQLite mémoire + FakeProvider (0 dépendances externes)
- Tests : health, users, logs, analyses, bulk, CSV, providers, security, rate limit, validation
- FakeProvider déterministe pour CI/CD

#### Added - CI/CD
- GitHub Actions workflow (`.github/workflows/ci.yml`)
  - Linting : `ruff`
  - Type checking : `mypy`
  - Tests : `pytest` avec coverage
  - Build Docker multi-arch
  - Trivy scan (image + filesystem)
  - Snyk scan (deps + code)
  - SARIF upload GitHub Security tab

---

### [0.9.0] — 2025-08-20 (Pre-Demo Alpha)

#### Added
- FastAPI app skeleton avec routers users/logs/analyses
- SQLAlchemy models : User, Log, Analyse
- PostgreSQL connection avec pooling
- Pydantic schemas : UserCreate, UserRead, LogCreate, LogRead, AnalyseRead
- Basic CSV parser (`debug_csv.py`)
- Dockerfile initial (python:3.11-slim)
- `compose.yaml` avec web + db

#### Fixed
- Docker Compose `version` attribute removed (deprecated)
- Flask import error (`re` module vs flask.re)
- Container startup crash (missing `app.run()` / `uvicorn`)

---

### [0.5.0] — 2025-08-10 (Sprint 1 - Foundation)

#### Added
- Git repo initialisé avec README, .gitignore, .env.example
- Architecture réseau documentée (client → API → DB → LLM)
- Scripts Bash d'initialisation et lancement
- Dockerfile de base
- Parser JSON/CSV pour logs

---

## Migration Guides

### Migration v1.0 → v1.1

**Breaking Changes :** Aucun (version MINOR)

**Nouvelles variables d'environnement requises :**
```env
# Rate Limiting (optionnel, défauts ci-dessous)
RATE_LIMIT_AUTH=10/minute
RATE_LIMIT_LOGS_WRITE=50/minute
RATE_LIMIT_ANALYZE=30/minute
RATE_LIMIT_DEFAULT=100/minute

# Request Size
MAX_REQUEST_SIZE=10485760  # 10 MB

# LLM Timeout
LLM_TIMEOUT_SECONDS=30
```

**Actions requises :**
1. Mettre à jour `docker-compose.production.yml` avec nouveaux resource limits
2. Régénérer secrets : `./scripts/init-docker-secrets.sh`
3. Rebuild : `docker compose -f compose.yaml -f docker-compose.production.yml build --no-cache`
4. Déployer : `docker compose -f compose.yaml -f docker-compose.production.yml up -d`

### Migration v0.9 → v1.0 (Premier Release)

**Breaking Changes :**
- Restructuration complète endpoints (API v1 stabilisée)
- Auth JWT infrastructure ajoutée (pas encore enforcée sur tous endpoints)
- Schéma DB : tables `users`, `logs`, `analyses` créées automatiquement
- Variables d'env : `SECRET_KEY` obligatoire, `DATABASE_URL` format changé

**Actions requises :**
1. Backup DB si existante
2. Nouveau `docker compose up --build` (recrée tables via `Base.metadata.create_all()`)
3. Régénérer secrets : `./scripts/init-docker-secrets.sh`
4. Migrer données manuellement si nécessaire (scripts custom)

---

## Deprecation Schedule

| Fonctionnalité | Dépréciée en | Retirée en | Remplacement |
|----------------|--------------|------------|--------------|
| `/auth/login` (501) | v1.1 | v1.3 | Implémentation complète v1.2 |
| `DATABASE_URL` en env direct | v1.1 | v2.0 | Docker Secrets + Vault |
| `LLM_PROVIDER` sans fallback | v1.1 | v1.3 | Fallback chain automatique |
| SQLite en prod | v1.0 | v1.0 | PostgreSQL uniquement |
| FakeProvider par défaut | v1.0 | v1.2 | OpenAI/Ollama config requis prod |

---

## API Stability Guarantees

### Stable (Garanti SemVer)
- Tous endpoints documentés dans `/openapi.json`
- Schémas de réponse Pydantic (`UserRead`, `LogRead`, `AnalyseRead`, `AnalysisResult`)
- Codes d'erreur HTTP standards + format `{"detail": "...", "errors?: [...]"}`
- Rate limiting headers
- Health check format

### Experimental (Peut changer sans préavis)
- Endpoints non documentés (`/metrics` si non configuré)
- Comportement FakeProvider (déterministe mais format interne)
- Ordre des logs dans `/logs` (tri par `created_at DESC` garanti)
- Champs `metadata` / `log_metadata` (réservé futur)

### Internal (Ne pas utiliser)
- Modèles SQLAlchemy directs (`User`, `Log`, `Analyse`)
- Fonctions privées (`_create_engine`, `get_llm_provider`, `hash_password`)
- Tables DB directes (utiliser l'API)

---

## Release Process

```bash
# 1. Sur branche release/v1.x.x
git checkout -b release/v1.2.0 develop

# 2. Mettre à jour version
#    - app.py: version="1.2.0"
#    - pyproject.toml / setup.cfg si applicable
#    - CHANGELOG.md: déplacer [Unreleased] → [1.2.0] - YYYY-MM-DD

# 3. Tests complets
pytest -v --cov=app --cov-fail-under=80
ruff check .
mypy app.py
bandit -r app.py
trivy image log-sentinel:1.2.0

# 4. Build & Push Docker
docker build -t log-sentinel:1.2.0 -t log-sentinel:latest .
docker push registry/log-sentinel:1.2.0
docker push registry/log-sentinel:latest

# 5. Merge et Tag
git checkout main
git merge --no-ff release/v1.2.0
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin main --tags

# 6. Cleanup
git branch -d release/v1.2.0
git push origin --delete release/v1.2.0

# 7. Backport develop
git checkout develop
git merge --no-ff main
git push origin develop
```

---

## Support Matrix

| Version | Statut | Support Actif | Security Patches | Fin de Vie |
|---------|--------|---------------|------------------|------------|
| 1.1.x | **Active** | ✅ Oui | ✅ Oui | 2026-03-15 |
| 1.0.x | Maintenance | ⚠️ Security only | ✅ Oui | 2025-12-01 |
| 0.x | Retired | ❌ Non | ❌ Non | 2025-09-01 |

---

## Liens Utiles

- **OpenAPI Spec** : `GET /openapi.json` (ou `/docs` pour Swagger UI)
- **GitHub Releases** : https://github.com/<org>/Log-Sentinel-API/releases
- **Docker Images** : `docker pull log-sentinel:<tag>`
- **Security Advisories** : GitHub Security Advisories + `SECURITY.md`
- **Migration Issues** : Label `migration` sur GitHub Issues