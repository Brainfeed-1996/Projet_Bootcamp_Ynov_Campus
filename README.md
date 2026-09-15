# Log Sentinel API

API **FastAPI** d'ingestion et d'analyse de logs sÃ©curisÃ©e, conÃ§ue pour un cours **DevSecOps** (Ynov â€” DÃ©fensive).

**Version** : `v1.1.0`  
**Stack** : Python 3.11+, FastAPI, PostgreSQL, Docker, Docker Compose, Trivy, Vault (optionnel).

---

## Table des matiÃ¨res

1. [PrÃ©requis](#prÃ©requis)
2. [Installation](#installation)
3. [Tests automatisÃ©s sans IA rÃ©elle](#tests-automatisÃ©s-sans-ia-rÃ©elle)
4. [DÃ©marrage rapide](#dÃ©marrage-rapide)
5. [SÃ©curitÃ© et secrets](#sÃ©curitÃ©-et-secrets)
6. [Endpoints](#endpoints)
7. [CI/CD et scan](#cicd-et-scan)
8. [DÃ©mo Demo Day](#dÃ©mo-demo-day)
9. [ProblÃ¨mes courants et solutions](#problÃ¨mes-courants-et-solutions)
10. [DÃ©finition of Done](#dÃ©finition-of-done)
11. [Support et nettoyage](#support-et-nettoyage)
12. [Architecture](#architecture)
13. [Contribuer](#contribuer)

---

## Architecture

Le projet suit une architecture en 3 couches :

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚   Client HTTP   â”‚â”€â”€â”€â”€â–¶â”‚   FastAPI App    â”‚â”€â”€â”€â”€â–¶â”‚  PostgreSQL DB  â”‚
â”‚   (curl/docs)   â”‚     â”‚   (app.py)       â”‚     â”‚  (users/logs)   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                â”‚
                        â”Œâ”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”
                        â”‚  LLM Providers â”‚
                        â”‚  (OpenAI/Ollamaâ”‚
                        â”‚   /Fake)       â”‚
                        â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Composants

- **app.py** : Application FastAPI principale avec authentification JWT
- **providers/** : Fournisseurs LLM (OpenAI, Ollama, Fake pour les tests)
- **schemas/** : ModÃ¨les Pydantic pour la validation
- **scripts/** : Scripts d'initialisation Docker et Vault
- **config/** : Configurations Vault (optionnel)
- **tests/** : Suite de tests complets

---

## Contribuer

1. Fork le dÃ©pÃ´t
2. CrÃ©er une branche feature (`git checkout -b feature/ma-fonctionnalitÃ©`)
3. Commit les changements (`git commit -m "feat: ma fonctionnalitÃ©"`)
4. Push la branche (`git push origin feature/ma-fonctionnalitÃ©`)
5. CrÃ©er une Pull Request

### Style des commits

Utiliser [Conventional Commits](https://www.conventionalcommits.org/) :
- `feat` : Nouvelle fonctionnalitÃ©
- `fix` : Correction de bug
- `docs` : Documentation
- `test` : Tests
- `chore` : Maintenance
- `refactor` : Refactoring
- `perf` : Performance
- `security` : SÃ©curitÃ©

---

## PrÃ©requis

- Python 3.11+ et `pip`
- Docker et Docker Compose (pour le conteneurisÃ©)
- Git

Variables d'environnement locales : copiez `.env.production.example` en `.env.production` et adaptez les secrets si vous lancez la production hors Docker.

---

## Installation

### Sans Docker (dÃ©veloppement local)

```bash
pip install -r requirements.txt
```

### Avec Docker (recommandÃ©)

```bash
./scripts/init-docker-secrets.sh
docker compose up --build -d
```

---

## Tests automatisÃ©s sans IA rÃ©elle

```bash
pytest -v
```

La suite utilise `LLM_PROVIDER=fake` par dÃ©faut et une base SQLite en mÃ©moire si `TESTING=1`. Aucune requÃªte vers OpenAI, Ollama ou PostgreSQL n'est exÃ©cutÃ©e.

- 16 tests couvrent : health, utilisateurs, validation, logs, analyse avec fournisseur factice, gestion d'erreurs et endpoints analyses.
- Fournisseurs IA robustifiÃ©s : validation JSON stricte, timeouts, URL sÃ©curisÃ©e, faux fournisseur dÃ©terministe.
- Aucun secret n'est affichÃ© ni commitÃ©.

---

## DÃ©marrage rapide

### 1. Initialiser les secrets Docker (dÃ©veloppement local)

```bash
./scripts/init-docker-secrets.sh
```

### 2. Lancer l'application

```bash
docker compose up --build -d
docker compose ps
curl http://localhost:5000/health
```

### 3. ArrÃªter

```bash
docker compose down -v
```

---

## SÃ©curitÃ© et secrets

- `.env` et `.env.production` sont **ignorÃ©s** par Git et Docker.
- Les secrets sont stockÃ©s dans `./secrets/*.txt` et montÃ©s via **Docker Secrets** (`compose.yaml`, `docker-compose.production.yml`).
- Aucune valeur par dÃ©faut n'est utilisÃ©e en production.
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

## Guide de Déploiement Production

Ce guide couvre le déploiement en production avec Docker Compose, HashiCorp Vault pour la gestion des secrets, et les variables d'environnement requises.

### Prérequis Production

- Docker Engine 24+ et Docker Compose v2+
- Serveur Linux (Ubuntu 22.04+, Debian 12+, RHEL 9+)
- 2 GB RAM minimum (4 GB recommandé)
- 10 GB espace disque pour l'application + base de données
- Accès réseau sortant pour pulls d'images et LLM providers (si pas en mode offline)
- Certificats TLS valides (Let's Encrypt ou PKI interne)

### Architecture de Déploiement

```
???????????????????     ???????????????????     ???????????????????
?   Load Balancer ???????   App Replicas  ???????   PostgreSQL    ?
?   (NGINX/Traefik)?     ?   (3+ pods)     ?     ?   (Primary)     ?
???????????????????     ???????????????????     ???????????????????
                                 ?                       ?
                                 ?                       ?
                        ???????????????????     ???????????????????
                        ?   Vault Agent   ?     ?   Replica/      ?
                        ?   (Sidecar)     ?     ?   Backup        ?
                        ???????????????????     ???????????????????
                                 ?
                                 ?
                        ???????????????????
                        ?  Observability  ?
                        ? (Loki/Prom/     ?
                        ?  Jaeger/Grafana)?
                        ???????????????????
```

### Fichiers de Configuration Requis

#### 1. `.env.production` (depuis `.env.production.example`)

```env
# Application
SECRET_KEY=<64-chars-hex-generate-with: openssl rand -hex 32>
LLM_PROVIDER=fake
LOG_LEVEL=INFO

# Database (remplis par Vault en prod, ici pour référence)
DATABASE_URL=postgresql://user:pass@db:5432/log_sentinel
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# LLM Providers (optionnel selon LLM_PROVIDER)
OPENAI_API_KEY=
OLLAMA_BASE_URL=http://ollama:11434

# Rate Limiting
RATE_LIMIT_AUTH=10/minute
RATE_LIMIT_LOGS_WRITE=50/minute
RATE_LIMIT_ANALYZE=30/minute
RATE_LIMIT_DEFAULT=100/minute

# Observability
PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus
JAEGER_AGENT_HOST=jaeger
JAEGER_AGENT_PORT=6831
LOKI_URL=http://loki:3100
```

#### 2. `docker-compose.production.yml`

```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    image: log-sentinel:latest
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    environment:
      - DATABASE_URL_FILE=/run/secrets/database_url
      - SECRET_KEY_FILE=/run/secrets/secret_key
      - LLM_PROVIDER=fake
      - LOG_LEVEL=INFO
    secrets:
      - database_url
      - secret_key
      - openai_api_key
    ports:
      - "5000:5000"
    depends_on:
      db:
        condition: service_healthy
      vault:
        condition: service_started
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"

  db:
    image: postgres:15-alpine
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
    environment:
      - POSTGRES_USER_FILE=/run/secrets/db_user
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
      - POSTGRES_DB=log_sentinel
    secrets:
      - db_user
      - db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d log_sentinel"]
      interval: 10s
      timeout: 5s
      retries: 5

  vault:
    image: hashicorp/vault:1.15
    deploy:
      resources:
        limits:
          memory: 256M
    environment:
      - VAULT_DEV_ROOT_TOKEN_FILE=/run/secrets/vault_root_token
      - VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200
    secrets:
      - vault_root_token
    ports:
      - "8200:8200"
    cap_add:
      - IPC_LOCK
    healthcheck:
      test: ["CMD", "vault", "status"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Observability stack (optionnel, déployer séparément en prod)
  loki:
    image: grafana/loki:2.9
    volumes:
      - loki_data:/loki
    ports:
      - "3100:3100"

  prometheus:
    image: prom/prometheus:v2.48
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:10.2
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD_FILE=/run/secrets/grafana_password
    secrets:
      - grafana_password
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"

  jaeger:
    image: jaegertracing/all-in-one:1.53
    ports:
      - "16686:16686"
      - "6831:6831/udp"

secrets:
  database_url:
    file: ./secrets/database_url.txt
  secret_key:
    file: ./secrets/secret_key.txt
  openai_api_key:
    file: ./secrets/openai_api_key.txt
  db_user:
    file: ./secrets/db_user.txt
  db_password:
    file: ./secrets/db_password.txt
  vault_root_token:
    file: ./secrets/vault_root_token.txt
  grafana_password:
    file: ./secrets/grafana_password.txt

volumes:
  postgres_data:
  loki_data:
  prometheus_data:
  grafana_data:
```

#### 3. `Dockerfile` (points clés production)

```dockerfile
FROM python:3.11-slim AS builder
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser
COPY --from=builder /root/.local /home/appuser/.local
WORKDIR /app
COPY --chown=appuser:appuser . .
USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "4"]
```

### Initialisation des Secrets (Production)

```bash
# 1. Créer le répertoire secrets (permissions strictes)
mkdir -p secrets
chmod 700 secrets

# 2. Générer les secrets (exemple)
openssl rand -hex 32 > secrets/secret_key.txt
openssl rand -hex 16 > secrets/db_password.txt
echo "log_sentinel" > secrets/db_user.txt
echo "postgresql://log_sentinel:$(cat secrets/db_password.txt)@db:5432/log_sentinel" > secrets/database_url.txt
echo "sk-your-openai-key" > secrets/openai_api_key.txt  # ou laisser vide pour fake
openssl rand -hex 16 > secrets/vault_root_token.txt
openssl rand -hex 16 > secrets/grafana_password.txt

# 3. Verrouiller les permissions
chmod 400 secrets/*.txt

# 4. Initialiser Vault (après démarrage)
docker compose -f compose.yaml -f docker-compose.production.yml up -d vault
sleep 10
docker compose -f compose.yaml -f docker-compose.production.yml exec vault vault kv put secret/log-sentinel \
  database_url="postgresql://log_sentinel:$(cat secrets/db_password.txt)@db:5432/log_sentinel" \
  secret_key="$(cat secrets/secret_key.txt)" \
  openai_api_key="$(cat secrets/openai_api_key.txt)"

# 5. Démarrer tous les services
docker compose -f compose.yaml -f docker-compose.production.yml up -d
```

### Déploiement avec Vault (Recommandé)

```bash
# 1. Démarrer Vault seul
docker compose -f compose.yaml -f docker-compose.production.yml up -d vault

# 2. Configurer Vault (une seule fois)
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=$(cat secrets/vault_root_token.txt)
vault auth enable approle
vault policy write log-sentinel - <<EOF
path "secret/data/log-sentinel" {
  capabilities = ["read"]
}
EOF

# 3. Créer un role AppRole pour l'app
vault write auth/approle/role/log-sentinel \
  token_policies="log-sentinel" \
  token_ttl=1h \
  token_max_ttl=4h

# 4. Récupérer RoleID et SecretID pour l'app
ROLE_ID=$(vault read -field=role_id auth/approle/role/log-sentinel/role-id)
SECRET_ID=$(vault write -f -field=secret_id auth/approle/role/log-sentinel/secret-id)

# 5. Stocker en secrets Docker pour l'app
echo "$ROLE_ID" > secrets/vault_role_id.txt
echo "$SECRET_ID" > secrets/vault_secret_id.txt
chmod 400 secrets/vault_*.txt
```

### Checklist Pré-Déploiement

- [ ] `.env.production` créé et validé
- [ ] Secrets générés dans `./secrets/` avec `chmod 400`
- [ ] `docker-compose.production.yml` validé (`docker compose config`)
- [ ] Images Docker buildées et scannées (`trivy image log-sentinel:latest`)
- [ ] Base de données initialisée (migrations si nécessaire)
- [ ] Vault configuré et policies appliquées
- [ ] Certificats TLS en place pour le reverse proxy
- [ ] Réseau Docker isolé (pas d'exposition DB/Loki/Prometheus sur host)
- [ ] Backup strategy testée (`pg_dump` vers stockage externe)
- [ ] Monitoring/Alerting configuré (Prometheus rules, Grafana dashboards)

### Commandes de Déploiement

```bash
# Build et déploiement initial
docker compose -f compose.yaml -f docker-compose.production.yml build --no-cache
docker compose -f compose.yaml -f docker-compose.production.yml up -d

# Vérification santé
docker compose -f compose.yaml -f docker-compose.production.yml ps
curl -f http://localhost:5000/health

# Mise à jour (zero-downtime avec replicas)
docker compose -f compose.yaml -f docker-compose.production.yml pull
docker compose -f compose.yaml -f docker-compose.production.yml up -d --no-deps web

# Rollback rapide
docker compose -f compose.yaml -f docker-compose.production.yml up -d --no-deps --scale web=3 log-sentinel:v1.0.0

# Logs
docker compose -f compose.yaml -f docker-compose.production.yml logs -f web

# Sauvegarde DB
docker compose -f compose.yaml -f docker-compose.production.yml exec db \
  pg_dump -U log_sentinel log_sentinel > backups/backup_$(date +%F).sql

# Nettoyage
docker compose -f compose.yaml -f docker-compose.production.yml down -v
```

### Variables d'Environnement Critiques

| Variable | Requis | Description | Source |
|----------|--------|-------------|--------|
| `SECRET_KEY` | Oui | Clé JWT (64 hex chars) | Vault / Docker Secret |
| `DATABASE_URL` | Oui | URL PostgreSQL complète | Vault / Docker Secret |
| `LLM_PROVIDER` | Oui | `fake` \| `openai` \| `ollama` | `.env.production` |
| `OPENAI_API_KEY` | Si OpenAI | Clé API OpenAI | Vault / Docker Secret |
| `DB_POOL_SIZE` | Non | Pool SQLAlchemy (défaut 10) | `.env.production` |
| `LOG_LEVEL` | Non | `DEBUG`/`INFO`/`WARNING`/`ERROR` | `.env.production` |

### Sécurisation Réseau

```yaml
# Dans docker-compose.production.yml - réseaux isolés
networks:
  frontend:
    driver: bridge
    internal: false  # LB only
  backend:
    driver: bridge
    internal: true   # Pas d'accès externe direct
  vault_net:
    driver: bridge
    internal: true

services:
  web:
    networks: [frontend, backend, vault_net]
  db:
    networks: [backend]
  vault:
    networks: [vault_net, backend]
  loki:
    networks: [backend]
  prometheus:
    networks: [backend]
  grafana:
    networks: [frontend, backend]
  jaeger:
    networks: [backend]
```

---

## Endpoints

Le provider LLM par dÃ©faut est `fake` (dÃ©terministe, sans rÃ©seau). Pour utiliser OpenAI ou Ollama, dÃ©finissez `LLM_PROVIDER=openai` ou `LLM_PROVIDER=ollama` avec les variables d'environnement requises.

```bash
# SantÃ©
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

## Référence API Complète

L'API est documentée via OpenAPI/Swagger à `/docs` (interface interactive) et `/openapi.json` (schéma brut).

### Authentification

Toutes les routes (sauf `/health` et `/docs`) nécessitent un token JWT dans l'en-tête `Authorization: Bearer <token>`. Obtenir un token via `POST /auth/login` (non implémenté dans cette version, voir `GET /users/{id}` pour lecture seule).

### Rate Limiting

| Endpoint | Limite |
|----------|--------|
| Authentification | 10 req/min |
| Création de logs | 50 req/min |
| Analyse IA | 30 req/min |
| Lecture (GET) | 100 req/min |

Headers de réponse : `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.

### Utilisateurs (`/users`)

| Méthode | Endpoint | Description | Corps de requête | Réponse succès |
|---------|----------|-------------|------------------|----------------|
| `GET` | `/users/{user_id}` | Récupérer un utilisateur par ID | — | `200 UserRead` |
| `POST` | `/users` | Créer un utilisateur | `UserCreate` | `201 UserRead` |
| `DELETE` | `/users/{user_id}` | Désactiver un utilisateur (soft delete) | — | `200 {id, status}` |

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
- `409` : Username ou email déjà existant
- `422` : Validation échouée (champs manquants, format invalide)

### Logs (`/logs`)

| Méthode | Endpoint | Description | Paramètres / Corps | Réponse succès |
|---------|----------|-------------|-------------------|----------------|
| `GET` | `/logs` | Lister les logs avec filtres | `level?`, `source?`, `limit? (1-1000, défaut 100)` | `200 [LogRead]` |
| `POST` | `/logs` | Créer un log | `LogCreate` | `201 LogRead` |
| `GET` | `/logs/{log_id}` | Récupérer un log par ID | — | `200 LogRead` |
| `POST` | `/logs/bulk` | Ingestion bulk JSON | `[LogCreate, ...]` (max 10000) | `200 BulkResult` |
| `POST` | `/logs/ingest-csv` | Ingestion CSV (multipart) | Fichier `.csv` avec colonnes `message`, `level?`, `source?` | `200 BulkResult` |
| `POST` | `/logs/{log_id}/analyze` | Analyser un log via LLM | — | `201 {id, log_id, result}` |

**LogCreate** :
```json
{
  "message": "string (1-4096 chars, requis)",
  "level": "string (DEBUG/INFO/WARNING/ERROR/CRITICAL, défaut INFO)",
  "source": "string (1-100 chars, défaut 'unknown')"
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
- `422` : Validation échouée, CSV invalide (colonne `message` requise)
- `502` : Provider LLM indisponible
- `503` : Base de données indisponible

### Analyses (`/analyses`)

| Méthode | Endpoint | Description | Corps de requête | Réponse succès |
|---------|----------|-------------|------------------|----------------|
| `GET` | `/analyses` | Lister les analyses | `limit? (1-1000, défaut 50)` | `200 [AnalyseRead]` |
| `POST` | `/analyses` | Créer une analyse manuelle | `{type, input_data?, result?}` | `201 AnalyseRead` |

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

### Santé et Monitoring (`/health`, `/metrics`)

| Méthode | Endpoint | Description | Réponse succès |
|---------|----------|-------------|----------------|
| `GET` | `/health` | Vérifier santé API + DB | `200 {status: "ok", database: "up"}` ou `503 {status: "error", database: "down"}` |
| `GET` | `/metrics` | Métriques Prometheus (si configuré) | Format Prometheus text |

### Codes d'erreur globaux

| Code | Signification |
|------|---------------|
| `200` | Succès (GET, PUT, DELETE) |
| `201` | Créé (POST) |
| `400` | Requête invalide (paramètres, validation métier) |
| `401` | Non authentifié (token manquant/invalide) |
| `403` | Interdit (CSRF, permissions insuffisantes) |
| `404` | Ressource introuvable |
| `409` | Conflit (doublon unique) |
| `413` | Payload trop volumineux |
| `422` | Erreur de validation Pydantic |
| `500` | Erreur interne serveur |
| `502` | Provider LLM indisponible |
| `503` | Service indisponible (DB down) |

### Exemples complets

**Créer un utilisateur** :
```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"bob","email":"bob@example.com","password":"SecurePass123"}'
```

**Créer un log** :
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
- Le scan Trivy est exÃ©cutÃ© dans le pipeline CI, pas dans l'image de build.

---

## DÃ©mo Demo Day

Consultez `DEMO_DAY.md` pour le support de dÃ©monstration :

- DurÃ©e : **6 minutes** de dÃ©mo + Q&A.
- RÃ©partition du temps de parole : **50/50** entre Presenter A et Presenter B.
- Plan minute par minute avec commandes et rÃ©sultats attendus.
- Plan de secours sans IA et sans Docker.

---

## DÃ©finition of Done

- [x] Projet repart sur une machine propre avec `git clone`, `./scripts/init-docker-secrets.sh`, `docker compose up`.
- [x] Tests automatisÃ©s passent sans accÃ¨s Ã  une vraie IA ni Ã  PostgreSQL.
- [x] Jeu de dÃ©monstration tient en six minutes et la parole est rÃ©partie Ã  50/50.
- [x] Code versionnÃ© et taguÃ© `v1.1.0` (depuis `v1.0.0`).
- [x] Documentation finale et support Demo Day fournis.
- [x] Secrets exclus de Git et de l'image Docker.
- [x] Fournisseurs IA validÃ©s sans rÃ©seau et avec erreurs explicites.

---

## ProblÃ¨mes courants et solutions

| ProblÃ¨me | Cause probable | Solution |
|----------|---------------|----------|
| `port 5000 already in use` | Un autre service utilise le port | `docker compose down` ou changer le port dans `compose.yaml` (ex: `5001:5000`) |
| `/health` retourne `503` â€” `database: down` | PostgreSQL pas encore prÃªt ou secrets manquants | VÃ©rifier `docker compose logs db` ; attendre le healthcheck ; relancer `./scripts/init-docker-secrets.sh` |
| `ModuleNotFoundError` | DÃ©pendances non installÃ©es | `pip install -r requirements.txt` (hors Docker) ou `docker compose up --build` |
| `/logs/1/analyze` retourne `502` | LLM externe (OpenAI/Ollama) injoignable | VÃ©rifier `LLM_PROVIDER` : mettre `fake` pour la dÃ©mo offline. Le fallback est automatique. |
| `pytest` Ã©choue avec `RuntimeError: DATABASE_URL` | `TESTING` non dÃ©fini en local | `TESTING=1 pytest -v` active SQLite en mÃ©moire |
| `.env` missing / secrets introuvables | Fichier `.env` absent ou non initialisÃ© | `cp .env.production.example .env.production` puis adapter les valeurs |
| Trivy trouve des CVE HIGH/CRITICAL | Image de base vulnÃ©rable | `docker pull python:3.11-slim` puis rebuild ; vÃ©rifier `.trivyignore` pour les exceptions justifiÃ©es |
| Tests Ã©chouent sur une machine propre | DÃ©marrage incomplet | `git clone`, `./scripts/init-docker-secrets.sh`, `docker compose up --build -d`, puis `pytest -v` |
| JSON invalide dans les requÃªtes curl | Guillemets ou apostrophes mal Ã©chappÃ©s | Utiliser les commandes du `demo-commands.sh` ou du fichier `DEMO_DAY.md` |
| `docker compose` non trouvÃ© | Docker non installÃ© ou non dÃ©marrÃ© | Installer Docker Desktop ; vÃ©rifier `docker --version` et `docker compose version` |

---

## Support et nettoyage

```bash
# Logs Docker
docker compose logs -f web
docker compose logs -f db

# RÃ©initialiser la base SQLite de test
rm -f test.sqlite test.sqlite-shm test.sqlite-wal
pytest -v
```

## Rate Limiting

L'API utilise un rate limiting pour protéger contre les abus :
- Authentification : 10 tentatives/minute
- Création de logs : 50/minute
- Analyse IA : 30/minute

## Changelog

### v1.1.0 (2025-09)
- Ajout du rate limiting
- Amélioration de la sécurité (headers, validation)
- Ajout des tests de performance
- Documentation complète

## Schéma de Base de Données

### Table users
- id: Identifiant unique
- username: Nom d'utilisateur (unique)
- email: Adresse email (unique)
- password_hash: Mot de passe haché
- role: Rôle (admin/writer/reader)
- is_active: Compte actif
- created_at: Date de création

### Table logs
- id: Identifiant unique
- occurred_at: Horodatage de l'événement
- level: Niveau (DEBUG/INFO/WARNING/ERROR/CRITICAL)
- message: Contenu du log
- source: Source du log
- log_metadata: Métadonnées JSON
- created_at: Date d'ingestion

## Contribuer

### Avant de committer
1. Exécuter les tests : `pytest tests/ -v`
2. Vérifier le linting : `ruff check .`
3. Vérifier les types : `mypy app.py`
4. Ne jamais commit de secrets

### Style des commits
- `feat` : Nouvelle fonctionnalité
- `fix` : Correction de bug
- `docs` : Documentation
- `test` : Tests
- `refactor` : Refactoring
- `chore` : Maintenance

## Versioning

L'API utilise le versioning par URL :
- `/api/v1/` : Version actuelle
- `/api/v2/` : Version future (développement)

La version est indiquée dans le schéma OpenAPI.

## Observabilité

### Stack
- **Logs** : Loki + Grafana
- **Metrics** : Prometheus + Grafana
- **Tracing** : Jaeger
- **Alerting** : Alertmanager

### Dashboard
- Disponibile à http://grafana:3000
- Identifiants : admin/admin
