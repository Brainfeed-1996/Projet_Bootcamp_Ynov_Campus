# Log Sentinel API

API **FastAPI** d'ingestion et d'analyse de logs sÃ©curisÃ©e, conÃ§ue pour un cours **DevSecOps** (Ynov — DÃ©fensive).

**Version** : `v1.0.0`  
**Stack** : Python 3.11+, FastAPI, PostgreSQL, Docker, Docker Compose, Trivy, Vault (optionnel).

> **Note** : La documentation reflÃ¨te l'Ã©tat rÃ©el de l'implÃ©mentation. Le rate limiting (constantes dÃ©finies) n'a pas encore de middleware actif ; les tests d'attente 429 Ã©choueront jusqu'Ã  implÃ©mentation.

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

> **Version API** : `v1.0.0` (voir `/openapi.json` ou `/docs` pour le schÃ©ma complet). Le rate limiting est prÃ©vu (constantes dans `app.py`) mais le middleware n'est pas encore implÃ©mentÃ©.

---

## SÃ©curitÃ© et secrets

- `.env` et `.env.production` sont **ignorÃ©s** par Git et Docker.
- Les secrets sont stockÃ©s dans `./secrets/*.txt` et montÃ©s via **Docker Secrets** (`compose.yaml`, `docker-compose.production.yml`).
- Aucune valeur par dÃ©faut n'est utilisÃ©e en production.
- Production : `docker compose -f compose.yaml -f docker-compose.production.yml up --build -d`.
- Vault : `docker compose -f compose.yaml -f docker-compose.vault.yml up --build -d`.

> **Rate Limiting** : Les constantes `RATE_LIMIT_AUTH=10/minute`, `RATE_LIMIT_LOGS_WRITE=50/minute`, `RATE_LIMIT_ANALYZE=30/minute`, `RATE_LIMIT_DEFAULT=100/minute` sont dÃ©finies dans `app.py` mais **le middleware n'est pas encore implÃ©mentÃ©**. Les tests `test_rate_limit.py` attendent un comportement 429 qui n'est pas actif.

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

### Procédures de Déploiement Avancées

#### Blue-Green Deployment

```bash
# 1. Déployer la nouvelle version (green)
docker compose -f compose.yaml -f docker-compose.production.yml up -d --no-deps --build web

# 2. Vérifier la santé du green
curl -f http://localhost:5000/health
docker compose -f compose.yaml -f docker-compose.production.yml ps web

# 3. Switch du traffic (via LB/NGINX)
# NGINX: upstream green { server <green-ip>:5000; } + active

# 4. Monitorer 15 minutes
docker compose -f compose.yaml -f docker-compose.production.yml logs -f web --since=15m

# 5. Si OK : promouvoir green ? production
#    (tag le conteneur green comme production)
docker tag log-sentinel:latest log-sentinel:v1.2.0

# 6. Si KO : rollback vers blue (v1.1.0)
docker compose -f compose.yaml -f docker-compose.production.yml up -d --no-deps --scale web=3 log-sentinel:v1.1.0
```

#### Canary Deployment

```yaml
# docker-compose.production.yml - Route 10% vers canary
# Via NGINX ou Traefik weighted routing:
# canary_weight: 10, stable_weight: 90
# Métriques à surveiller : erreurs, latence, CPU/mémoire
```

#### Disaster Recovery

| Scénario | RTO (Recovery Time) | RPO (Recovery Point) | Procédure |
|----------|---------------------|----------------------|-----------|
| Perte totale DB | < 15 min | < 1h | Restaurer depuis backup S3 + WAL |
| Perte totale app | < 5 min | 0 | Redéployer Docker Compose |
| Perte totale Vault | < 30 min | < 1h | Restaurer depuis snapshot Vault |
| Région entière | < 1h | < 4h | Failover multi-région (plan B) |
| Ransomware | < 2h | < 24h | Restore depuis backup air-gapped |

**Procédure de Restauration Complète :**
```bash
# 1. Arrêter l'environnement
docker compose -f compose.yaml -f docker-compose.production.yml down

# 2. Restaurer la base depuis backup
docker volume create postgres_data_restored
docker run --rm -v postgres_data_restored:/var/lib/postgresql/data \
  -v /backups:/backups postgres:15-alpine \
  bash -c "pg_restore -U log_sentinel -d log_sentinel /backups/backup_latest.sql"

# 3. Restaurer les secrets
cp backups/secrets_backup_*.txt secrets/
chmod 400 secrets/*.txt

# 4. Redémarrer
docker compose -f compose.yaml -f docker-compose.production.yml up -d

# 5. Vérifications
curl -f http://localhost:5000/health
docker compose -f compose.yaml -f docker-compose.production.yml ps
```

#### Scaling Horizontal

```bash
# Scale web (ajouter des replicas)
docker compose -f compose.yaml -f docker-compose.production.yml up -d --scale web=6

# Scale db (read replicas via Pooler)
# PgBouncer ou Supavisor pour connection pooling
docker compose -f compose.yaml -f docker-compose.production.yml up -d --scale db=1

# Vérifier la distribution
docker compose -f compose.yaml -f docker-compose.production.yml ps -a
```

#### Tuning de Performance

```bash
# 1. Connection pooling (PgBouncer)
docker volume create pgbouncer_data
docker compose -f compose.yaml -f docker-compose.production.yml up -d pgbouncer

# 2. Monitoring des requêtes lentes
docker exec db psql -U postgres -d log_sentinel -c "
  SELECT query, mean_exec_time, calls
  FROM pg_stat_statements
  ORDER BY mean_exec_time DESC
  LIMIT 10;"

# 3. VACUUM et ANALYZE programmés
docker exec db psql -U postgres -d log_sentinel -c "VACUUM ANALYZE logs;"
docker exec db psql -U postgres -d log_sentinel -c "VACUUM ANALYZE analyses;"

# 4. Index recommandés pour gros volumes
docker exec db psql -U postgres -d log_sentinel -c "
  CREATE INDEX IF NOT EXISTS idx_logs_created_at_2
  ON logs(created_at DESC) WHERE level = 'ERROR';"
```

#### Rolling Update (zero-downtime)

```bash
# 1. Pull la nouvelle image
docker compose -f compose.yaml -f docker-compose.production.yml pull web

# 2. Mise à jour progressive (1 par 1)
docker compose -f compose.yaml -f docker-compose.production.yml up -d --no-deps web

# 3. Chaque conteneur passe par :
#    - healthcheck OK ? reste
#    - healthcheck FAIL ? rollback automatique

# 4. Vérifier après chaque vague
curl -f http://localhost:5000/health
```

### Configuration SSL/TLS (Reverse Proxy)

```nginx
# nginx.conf - Frontend TLS termination
server {
    listen 443 ssl http2;
    server_name api.logsentinel.io;

    ssl_certificate /etc/letsencrypt/live/api.logsentinel.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.logsentinel.io/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

    location / {
        proxy_pass http://web:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTP ? HTTPS redirect
server {
    listen 80;
    server_name api.logsentinel.io;
    return 301 https://$server_name$request_uri;
}
```

### Variables d'Environnement de Production (Récapitulatif)

| Variable | Requis | Valeur Prod | Source | Exemple |
|----------|--------|-------------|--------|---------|
| `SECRET_KEY` | Oui | 64 hex chars | Vault | `openssl rand -hex 32` |
| `DATABASE_URL` | Oui | PostgreSQL prod | Vault | `postgresql://user:pass@db:5432/log_sentinel` |
| `DB_USER` | Oui | Utilisateur DB | Vault/Docker Secret | `log_sentinel` |
| `DB_PASSWORD` | Oui | Mot de passe fort | Vault/Docker Secret | `openssl rand -hex 16` |
| `DB_POOL_SIZE` | Non | 20 | `.env.production` | `20` |
| `DB_MAX_OVERFLOW` | Non | 40 | `.env.production` | `40` |
| `LLM_PROVIDER` | Oui | `fake`\|`openai`\|`ollama` | `.env.production` | `fake` |
| `OPENAI_API_KEY` | Si OpenAI | Clé API valide | Vault/Docker Secret | `sk-...` |
| `OLLAMA_BASE_URL` | Si Ollama | URL interne | `.env.production` | `http://ollama:11434` |
| `RATE_LIMIT_AUTH` | Non | 10/minute | `.env.production` | `10/minute` |
| `RATE_LIMIT_LOGS_WRITE` | Non | 50/minute | `.env.production` | `50/minute` |
| `RATE_LIMIT_ANALYZE` | Non | 30/minute | `.env.production` | `30/minute` |
| `RATE_LIMIT_DEFAULT` | Non | 100/minute | `.env.production` | `100/minute` |
| `LOG_LEVEL` | Non | `INFO` | `.env.production` | `INFO` |
| `PROMETHEUS_MULTIPROC_DIR` | Si metrics | Chemin tmp | `.env.production` | `/tmp/prometheus` |
| `JAEGER_AGENT_HOST` | Si tracing | Service name | `.env.production` | `jaeger` |
| `JAEGER_AGENT_PORT` | Si tracing | Port | `.env.production` | `6831` |
| `LOKI_URL` | Si logs agg | Service URL | `.env.production` | `http://loki:3100` |

### Structure des Secrets Docker (Production)

```
secrets/
??? database_url.txt       # URL PostgreSQL complète (chmod 400)
??? secret_key.txt         # Clé JWT (chmod 400)
??? openai_api_key.txt     # Clé API OpenAI (chmod 400, optionnel)
??? db_user.txt            # Utilisateur DB (chmod 400)
??? db_password.txt        # Mot de passe DB (chmod 400)
??? vault_root_token.txt   # Token root Vault (chmod 400)
??? grafana_password.txt   # Mot de passe Grafana (chmod 400)
```

### Verification Post-Déploiement

```bash
# 1. Santé globale
curl -f http://localhost:5000/health
# {"status":"ok","database":"up"}

# 2. Vérifier tous les conteneurs
docker compose -f compose.yaml -f docker-compose.production.yml ps
# TOUS doivent être "healthy"

# 3. Vérifier les secrets montés
docker compose -f compose.yaml -f docker-compose.production.yml exec web \
  ls -la /run/secrets/

# 4. Vérifier non-root
docker compose -f compose.yaml -f docker-compose.production.yml exec web \
  whoami
# Doit retourner "appuser"

# 5. Vérifier headers de sécurité
curl -I https://api.logsentinel.io | grep -i "x-content\|x-frame\|x-xss\|strict"

# 6. Vérifier rate limiting
for i in $(seq 1 15); do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5000/health; done
# Les 11e+ doivent retourner 429
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

L'authentification JWT est configurée (middleware, expiration 30 min, bcrypt cost 12). L'endpoint `POST /auth/login` est **non implémenté** dans cette version ; les routes protégées ne sont pas encore appliquées globalement. Voir `GET /users/{id}` pour lecture seule sans token.

### Rate Limiting

> **Non implémenté** : Les constantes `RATE_LIMIT_AUTH=10/minute`, `RATE_LIMIT_LOGS_WRITE=50/minute`, `RATE_LIMIT_ANALYZE=30/minute`, `RATE_LIMIT_DEFAULT=100/minute` sont définies dans `app.py` mais **aucun middleware n'est actif**. Les headers `X-RateLimit-*` ne sont pas retournés. Les tests `test_rate_limit.py` attendent un comportement 429 qui n'existe pas encore.

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
| `GET` | `/logs/export` | Export CSV streaming (tous logs) | `chunk_size? (défaut 100)` | `text/csv` stream |
| `GET` | `/logs/report` | Export CSV paginé avec filtres | `page?`, `page_size?`, `level?`, `source?` | `text/csv` stream |

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

### Admin (`/admin`)

| Méthode | Endpoint | Description | Corps de requête | Réponse succès |
|---------|----------|-------------|------------------|----------------|
| `POST` | `/admin/cleanup` | Supprimer logs/analyses > N jours | `days? (défaut 90)` | `200 {logs_deleted, analyses_deleted}` |
| `POST` | `/admin/alerts` | Envoyer email alerte critique | `AlertPayload` | `200 {status: "sent"}` |

> **Note** : Routes protégées par `X-API-Key` (service-à-service). Voir `API_KEYS` dans `app.py`.

### Webhooks (`/webhooks`)

Seul `POST /webhooks/log-created` est implémenté (reçoit notifications log créé). Les autres routes listées ci-dessous sont **non implémentées**.

| Méthode | Endpoint | Description | Statut |
|---------|----------|-------------|--------|
| `POST` | `/webhooks/log-created` | Réception événement log créé | ? Implémenté |
| `GET` | `/webhooks` | Lister webhooks | ? Non implémenté |
| `POST` | `/webhooks` | Créer webhook | ? Non implémenté |
| `GET` | `/webhooks/{id}` | Récupérer webhook | ? Non implémenté |
| `DELETE` | `/webhooks/{id}` | Supprimer webhook | ? Non implémenté |
| `POST` | `/webhooks/{id}/test` | Tester webhook | ? Non implémenté |

### Santé et Monitoring (`/health`)

| Méthode | Endpoint | Description | Réponse succès |
|---------|----------|-------------|----------------|
| `GET` | `/health` | Vérifier santé API + DB | `200 {status: "ok", database: "up"}` ou `503 {status: "error", database: "down"}` |

> **Note** : `/metrics` et `/metrics/summary` (Prometheus) ne sont **pas implémentés** dans cette version.

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
| `GET` | `/export/analyses` | Exporter les analyses en JSON/CSV | `format? (json/csv)`, `severity?`, `from?`, `to?` | `200` (fichier) |
| `GET` | `/export/users` | Exporter les utilisateurs | `format? (json/csv)` | `200` (fichier) |

**Export CSV — Headers de réponse :**
```
Content-Disposition: attachment; filename="logs_2025-09-15.csv"
Content-Type: text/csv; charset=utf-8
```

**Exemple — Export logs en CSV :**
```bash
curl -X GET http://localhost:5000/export/logs?format=csv&level=ERROR \
  -H "Authorization: Bearer <token>" \
  -o logs_export.csv
```

**Exemple — Export analyses en JSON :**
```bash
curl -X GET http://localhost:5000/export/analyses?format=json&severity=HIGH \
  -H "Authorization: Bearer <token>" \
  -o analyses_export.json
```

### Rapport (`/report`)

| Méthode | Endpoint | Description | Corps de requête | Réponse succès |
|---------|----------|-------------|------------------|----------------|
| `POST` | `/report/generate` | Générer un rapport PDF/HTML | `{type, date_from?, date_to?, format?}` | `201 {report_id, url}` |
| `GET` | `/report/{report_id}` | Télécharger un rapport | — | `200` (fichier) |
| `GET` | `/report/{report_id}/status` | Statut de génération | — | `200 {status, progress}` |

**Generate Report :**
```json
{
  "type": "security_audit | compliance | activity | custom",
  "date_from": "ISO8601 datetime (optionnel)",
  "date_to": "ISO8601 datetime (optionnel)",
  "format": "pdf | html (défaut: pdf)",
  "filters": {
    "levels": ["ERROR", "CRITICAL"],
    "sources": ["api", "postgres"],
    "categories": ["DATABASE", "SECURITY"]
  }
}
```

**Report Read :**
```json
{
  "id": "uuid",
  "type": "security_audit",
  "format": "pdf",
  "status": "ready | generating | failed",
  "url": "/report/<uuid>/download",
  "created_at": "ISO8601 datetime",
  "expires_at": "ISO8601 datetime (7 jours)",
  "size_bytes": 123456
}
```

**Exemple :**
```bash
curl -X POST http://localhost:5000/report/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"type": "security_audit", "format": "pdf", "date_from": "2025-09-01T00:00:00Z"}'
```

### Webhooks (`/webhooks`)

| Méthode | Endpoint | Description | Corps de requête | Réponse succès |
|---------|----------|-------------|------------------|----------------|
| `GET` | `/webhooks` | Lister les webhooks | — | `200 [WebhookRead]` |
| `POST` | `/webhooks` | Créer un webhook | `WebhookCreate` | `201 WebhookRead` |
| `GET` | `/webhooks/{webhook_id}` | Récupérer un webhook | — | `200 WebhookRead` |
| `DELETE` | `/webhooks/{webhook_id}` | Supprimer un webhook | — | `200 {id, status}` |
| `POST` | `/webhooks/{webhook_id}/test` | Tester un webhook | — | `200 {success, http_status}` |

**WebhookCreate :**
```json
{
  "url": "https://hooks.example.com/log-sentinel",
  "events": ["log.created", "log.analyzed", "alert.triggered"],
  "secret": "webhook-secret-key",
  "active": true,
  "retry_policy": {
    "max_retries": 3,
    "backoff_multiplier": 2,
    "initial_delay_ms": 1000
  }
}
```

**WebhookRead :**
```json
{
  "id": "uuid",
  "url": "https://hooks.example.com/log-sentinel",
  "events": ["log.created", "log.analyzed"],
  "active": true,
  "created_at": "ISO8601 datetime",
  "last_triggered_at": "ISO8601 datetime | null",
  "last_http_status": 200
}
```

**Payload envoyé aux webhooks :**
```json
{
  "event": "log.created",
  "timestamp": "ISO8601 datetime",
  "data": {
    "id": 42,
    "level": "ERROR",
    "message": "Database connection timeout",
    "source": "postgres"
  },
  "signature": "sha256=..."
}
```

**Signature de vérification (HMAC-SHA256) :**
```python
import hmac, hashlib
signature = hmac.new(
    secret.encode(), payload.encode(), hashlib.sha256
).hexdigest()
# Header : X-Webhook-Signature: sha256=...
```

### Métriques (`/metrics`)

| Méthode | Endpoint | Description | Réponse succès |
|---------|----------|-------------|----------------|
| `GET` | `/metrics` | Métriques Prometheus | Format Prometheus text |
| `GET` | `/metrics/summary` | Résumé JSON des métriques clés | `200 {summary}` |

**Résumé JSON :**
```json
{
  "timestamp": "ISO8601 datetime",
  "api": {
    "total_requests": 15420,
    "requests_per_minute": 42.3,
    "error_rate_percent": 0.8,
    "p50_response_time_ms": 25,
    "p95_response_time_ms": 120,
    "p99_response_time_ms": 350
  },
  "database": {
    "status": "up",
    "connections_active": 8,
    "connections_idle": 2,
    "total_queries": 45230,
    "slow_queries": 3,
    "cache_hit_rate": 0.92
  },
  "logs": {
    "total_count": 12847,
    "by_level": { "DEBUG": 2100, "INFO": 8900, "WARNING": 1200, "ERROR": 540, "CRITICAL": 107 },
    "ingested_last_hour": 342
  },
  "analyses": {
    "total_count": 12640,
    "by_severity": { "LOW": 8900, "MEDIUM": 2500, "HIGH": 1100, "CRITICAL": 140 },
    "by_provider": { "fake": 12640, "openai": 0, "ollama": 0 }
  }
}
```

**Exemple — Requête et parse Prometheus :**
```bash
curl -s http://localhost:5000/metrics | grep http_requests_total
# http_requests_total{method="GET",endpoint="/logs",status="200"} 14520
curl -s http://localhost:5000/metrics | grep http_request_duration_seconds
# http_request_duration_seconds{p55=0.025,p95=0.120,p99=0.350}
```

**Exemple — Résumé des métriques :**
```bash
curl -X GET http://localhost:5000/metrics/summary \
  -H "Authorization: Bearer <token>"
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

Le projet utilise **PostgreSQL 15+** en production et **SQLite en mémoire** pour les tests (`TESTING=1`). Les tables sont créées automatiquement au démarrage via `SQLAlchemy Base.metadata.create_all()`.

### Diagramme Entité-Relation

```
???????????????????       ???????????????????       ???????????????????
?     users       ?       ?     logs        ?       ?   analyses      ?
???????????????????       ???????????????????       ???????????????????
? PK  id          ?       ? PK  id          ?       ? PK  id          ?
?     username    ????????? FK  user_id?    ?       ? FK  log_id      ?
?     email       ?       ?     level       ??????????     type        ?
?     password_hash?      ?     message     ?       ?     input_data  ?
?     role        ?       ?     source      ?       ?     result      ?
?     is_active   ?       ?     log_metadata?       ?     created_at  ?
?     created_at  ?       ?     created_at  ?       ???????????????????
???????????????????       ???????????????????
         ?                        ?
         ?                        ? (1 log ? N analyses)
         ?                        ?
   Soft delete             Analyse LLM
   (is_active=false)       ou manuelle
```

> **Note** : La relation `users ? logs` via `user_id` est prévue dans le modèle mais pas encore implémentée dans l'API actuelle (logs non attachés à un user). Voir roadmap v1.2.

---

### Table `users`

Stocke les comptes utilisateurs pour l'authentification et l'autorisation.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Identifiant unique |
| `username` | `VARCHAR(50)` | `NOT NULL`, `UNIQUE` | Nom d'utilisateur (3-50 chars) |
| `email` | `VARCHAR(120)` | `NOT NULL`, `UNIQUE` | Email valide (max 120 chars) |
| `password_hash` | `VARCHAR(256)` | `NOT NULL` | Hash bcrypt (cost 12) |
| `role` | `VARCHAR(20)` | `NOT NULL`, `DEFAULT 'reader'` | Rôle : `admin`, `writer`, `reader` |
| `is_active` | `BOOLEAN` | `NOT NULL`, `DEFAULT true` | Soft delete flag |
| `created_at` | `TIMESTAMP` | `NOT NULL`, `DEFAULT now()` | Date de création UTC |

**Index :**
```sql
-- Créés automatiquement par UNIQUE constraints
CREATE UNIQUE INDEX ix_users_username ON users(username);
CREATE UNIQUE INDEX ix_users_email ON users(email);

-- Recommandé pour requêtes fréquentes
CREATE INDEX ix_users_is_active ON users(is_active);
CREATE INDEX ix_users_created_at ON users(created_at DESC);
```

**Exemple d'insertion :**
```sql
INSERT INTO users (username, email, password_hash, role)
VALUES (
  'alice',
  'alice@example.com',
  '$2b$12$...',  -- bcrypt hash
  'writer'
);
```

---

### Table `logs`

Stocke les événements de logs ingérés (JSON, CSV, bulk).

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Identifiant unique |
| `level` | `VARCHAR(20)` | `NOT NULL` | Niveau : `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `message` | `TEXT` | `NOT NULL` | Contenu du log (max 4096 chars) |
| `source` | `VARCHAR(100)` | `DEFAULT 'unknown'` | Source/origine du log |
| `log_metadata` | `JSONB` | `NULLABLE` | Métadonnées additionnelles (extensible) |
| `created_at` | `TIMESTAMP` | `NOT NULL`, `DEFAULT now()` | Date d'ingestion UTC |

**Index :**
```sql
-- Index pour filtres fréquents (GET /logs?level=...&source=...)
CREATE INDEX ix_logs_level ON logs(level);
CREATE INDEX ix_logs_source ON logs(source);
CREATE INDEX ix_logs_created_at ON logs(created_at DESC);

-- Index composite pour filtres combinés
CREATE INDEX ix_logs_level_created_at ON logs(level, created_at DESC);
CREATE INDEX ix_logs_source_created_at ON logs(source, created_at DESC);

-- Index GIN pour recherche JSONB (si log_metadata utilisé)
CREATE INDEX ix_logs_metadata_gin ON logs USING GIN (log_metadata);
```

**Contraintes de validation (appliquées par Pydantic avant INSERT) :**
- `level` ? `{DEBUG, INFO, WARNING, ERROR, CRITICAL}`
- `message` : 1-4096 caractères, non vide
- `source` : 1-100 caractères, non vide

**Exemple d'insertion :**
```sql
INSERT INTO logs (level, message, source, log_metadata)
VALUES (
  'ERROR',
  'Database connection pool exhausted',
  'postgres',
  '{"pool_size": 20, "active": 20, "waiting": 5}'::jsonb
);
```

---

### Table `analyses`

Stocke les résultats d'analyse des logs (via LLM ou manuelles).

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Identifiant unique |
| `log_id` | `INTEGER` | `NOT NULL`, `REFERENCES logs(id)` | FK vers table logs |
| `type` | `VARCHAR(50)` | `NOT NULL`, `DEFAULT 'log_analysis'` | Type d'analyse |
| `input_data` | `TEXT` | `NULLABLE` | Log message analysé (copie) |
| `result` | `TEXT` | `NULLABLE` | Résultat JSON (AnalysisResult schema) |
| `created_at` | `TIMESTAMP` | `NOT NULL`, `DEFAULT now()` | Date d'analyse UTC |

**Index :**
```sql
-- FK index (requis pour JOIN performances)
CREATE INDEX ix_analyses_log_id ON analyses(log_id);

-- Tri par date (GET /analyses ORDER BY created_at DESC)
CREATE INDEX ix_analyses_created_at ON analyses(created_at DESC);

-- Index composite pour requêtes "analyses récentes d'un log"
CREATE INDEX ix_analyses_log_id_created_at ON analyses(log_id, created_at DESC);
```

**Schéma `result` (JSON stocké dans `TEXT`) :**
```json
{
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "category": "AUTH|NETWORK|SYSTEM|APPLICATION|DATABASE|SECURITY",
  "summary": "Brève description de l'incident",
  "recommendations": [
    "Action corrective 1",
    "Action corrective 2"
  ],
  "provider": "fake|openai|ollama"
}
```

**Exemple d'insertion :**
```sql
INSERT INTO analyses (log_id, type, input_data, result)
VALUES (
  42,
  'log_analysis',
  'Database connection pool exhausted',
  '{"severity":"HIGH","category":"DATABASE","summary":"Pool épuisé","recommendations":["Augmenter pool_size","Optimiser requêtes"],"provider":"fake"}'
);
```

---

### Relations et Intégrité Référentielle

```sql
-- Relation analyses ? logs (1 log = N analyses)
ALTER TABLE analyses
ADD CONSTRAINT fk_analyses_log_id
FOREIGN KEY (log_id) REFERENCES logs(id)
ON DELETE CASCADE;  -- Si log supprimé, analyses associées supprimées
```

> **Note** : `ON DELETE CASCADE` assure la cohérence. La suppression d'un log (soft ou hard) entraîne la suppression de ses analyses.

---

### Migrations et Évolutions

Le projet n'utilise pas encore d'outil de migration formel (Alembic). Les changements de schéma sont gérés par :

1. **Modification des modèles SQLAlchemy** dans `app.py`
2. **Redémarrage de l'app** ? `Base.metadata.create_all()` crée tables manquantes
3. **Migrations manuelles** pour changements destructifs (ALTER TABLE, DROP COLUMN)

#### Roadmap Migrations (v1.2+)
- [ ] Ajouter `user_id` FK sur `logs` (authorship)
- [ ] Ajouter `alerts` table pour seuils de sévérité
- [ ] Partitionner `logs` par mois (pg_partman)
- [ ] Ajouter `full-text search` via `tsvector` + GIN index

---

### Requêtes Utiles pour Administration

```sql
-- Statistiques globales
SELECT
  (SELECT count(*) FROM users WHERE is_active) as active_users,
  (SELECT count(*) FROM logs) as total_logs,
  (SELECT count(*) FROM analyses) as total_analyses,
  (SELECT count(*) FROM analyses WHERE result::jsonb->>'severity' IN ('HIGH','CRITICAL')) as critical_alerts;

-- Logs par niveau (dernières 24h)
SELECT level, count(*)
FROM logs
WHERE created_at > now() - interval '24 hours'
GROUP BY level
ORDER BY count(*) DESC;

-- Top 10 sources de logs
SELECT source, count(*) as cnt
FROM logs
GROUP BY source
ORDER BY cnt DESC
LIMIT 10;

-- Analyses par provider
SELECT result::jsonb->>'provider' as provider, count(*)
FROM analyses
GROUP BY provider;

-- Logs sans analyse (candidats pour analyse)
SELECT l.id, l.level, l.message, l.created_at
FROM logs l
LEFT JOIN analyses a ON a.log_id = l.id
WHERE a.id IS NULL
ORDER BY l.created_at DESC
LIMIT 50;

-- Taille tables et index
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
  pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

### Sauvegarde et Restauration

```bash
# Backup complet (structure + données)
docker compose exec db pg_dump -U log_sentinel -d log_sentinel > backup_full_$(date +%F).sql

# Backup données seulement (pour restauration sur schéma existant)
docker compose exec db pg_dump -U log_sentinel -d log_sentinel --data-only > backup_data_$(date +%F).sql

# Backup table spécifique
docker compose exec db pg_dump -U log_sentinel -d log_sentinel -t logs > backup_logs_$(date +%F).sql

# Restauration
docker compose exec -T db psql -U log_sentinel -d log_sentinel < backup_full_2025-09-15.sql

# Restauration table unique (attention: TRUNCATE d'abord)
docker compose exec db psql -U log_sentinel -d log_sentinel -c "TRUNCATE logs, analyses RESTART IDENTITY CASCADE;"
docker compose exec -T db psql -U log_sentinel -d log_sentinel < backup_logs_2025-09-15.sql
```

---

### Configuration PostgreSQL Recommandée (Production)

```postgresql
# postgresql.conf (via Docker config ou volume)
shared_buffers = 256MB                    # 25% RAM
effective_cache_size = 1GB                # 75% RAM
work_mem = 16MB                           # Par opération tri/hash
maintenance_work_mem = 256MB              # VACUUM, CREATE INDEX
max_connections = 100                     # Selon pool taille
random_page_cost = 1.1                    # SSD
effective_io_concurrency = 200            # SSD NVMe
wal_buffers = 16MB
checkpoint_completion_target = 0.9
max_wal_size = 4GB
min_wal_size = 1GB
```

---

### Vues Métier

#### Statistiques Globales (Dashboard)

```sql
CREATE VIEW v_dashboard_stats AS
SELECT
  (SELECT count(*) FROM users WHERE is_active) as active_users,
  (SELECT count(*) FROM logs) as total_logs,
  (SELECT count(*) FROM analyses) as total_analyses,
  (SELECT count(*) FROM analyses WHERE result::jsonb->>'severity' IN ('HIGH','CRITICAL')) as critical_alerts,
  (SELECT count(*) FROM logs WHERE created_at > now() - interval '24 hours') as logs_24h,
  now() as updated_at;
```

#### Top Sources de Logs

```sql
CREATE VIEW v_top_sources AS
SELECT
  source,
  count(*) as log_count,
  count(*) FILTER (WHERE level = 'ERROR') as error_count,
  count(*) FILTER (WHERE level = 'CRITICAL') as critical_count,
  max(created_at) as last_seen
FROM logs
GROUP BY source
ORDER BY log_count DESC;
```

#### Logs sans Analyse (Candidats)

```sql
CREATE VIEW v_unanalyzed_logs AS
SELECT
  l.id,
  l.level,
  l.message,
  l.source,
  l.created_at,
  l.log_metadata
FROM logs l
LEFT JOIN analyses a ON a.log_id = l.id
WHERE a.id IS NULL
ORDER BY l.created_at DESC;
```

### Automatisation de la Rétention des Données

```sql
-- Function: supprimer les données expirées
CREATE OR REPLACE FUNCTION purge_old_data()
RETURNS void AS $$
BEGIN
  -- Supprimer les analyses de logs > 90 jours
  DELETE FROM analyses
  WHERE log_id NOT IN (
    SELECT id FROM logs WHERE created_at > now() - interval '90 days'
  );

  -- Supprimer les logs > 90 jours
  DELETE FROM logs
  WHERE created_at < now() - interval '90 days';

  -- Les utilisateurs sont conservés 365 jours (conforme RGPD)
  DELETE FROM users
  WHERE is_active = true
    AND created_at < now() - interval '365 days';

  RAISE NOTICE 'Purge terminée : %, %, % rows',
    (SELECT count(*) FROM logs WHERE created_at < now() - interval '90 days'),
    (SELECT count(*) FROM analyses WHERE log_id NOT IN (SELECT id FROM logs WHERE created_at > now() - interval '90 days')),
    (SELECT count(*) FROM users WHERE is_active = true AND created_at < now() - interval '365 days');
END;
$$ LANGUAGE plpgsql;

-- Job pg_cron pour exécution quotidienne (si pg_cron installé)
SELECT cron.schedule('purge-old-data', '0 3 * * *', 'SELECT purge_old_data()');
```

### Procédures de Maintenance

#### Reindex et VACUUM Programmé

```sql
-- Function: maintenance hebdomadaire
CREATE OR REPLACE FUNCTION weekly_maintenance()
RETURNS void AS $$
BEGIN
  -- VACUUM ANALYZE sur les tables principales
  VACUUM ANALYZE logs;
  VACUUM ANALYZE analyses;
  VACUUM ANALYZE users;

  -- Reindex des index les plus utilisés
  REINDEX INDEX ix_logs_level_created_at;
  REINDEX INDEX ix_logs_source_created_at;
  REINDEX INDEX ix_analyses_log_id_created_at;

  RAISE NOTICE 'Maintenance hebdomadaire terminée';
END;
$$ LANGUAGE plpgsql;

-- Schedule : chaque dimanche à 2h du matin
SELECT cron.schedule('weekly-maintenance', '0 2 * * 0', 'SELECT weekly_maintenance()');
```

### Monitoring de l'Intégrité de la Base

```sql
-- Vérification de l'intégrité des tables
SELECT
  schemaname,
  tablename,
  pg_relation_size(schemaname || '.' || tablename) as size_bytes,
  pg_size_pretty(pg_relation_size(schemaname || '.' || tablename)) as size_pretty,
  pg_stat_user_tables.relpages as pages,
  pg_stat_user_tables.seq_scan as seq_scans,
  pg_stat_user_tables.idx_scan as idx_scans,
  pg_stat_user_tables.n_tup_ins as inserts,
  pg_stat_user_tables.n_tup_upd as updates,
  pg_stat_user_tables.n_tup_del as deletes
FROM pg_stat_user_tables
JOIN pg_class ON pg_class.relname = pg_stat_user_tables.relname
WHERE schemaname = 'public'
ORDER BY pg_relation_size(schemaname || '.' || tablename) DESC;

-- Vérifier les tables sans index
SELECT
  t.relname as table_name,
  c.relname as index_name,
  a.attname as column_name
FROM pg_class t
JOIN pg_attribute a ON a.attrelid = t.oid
LEFT JOIN pg_index i ON i.indrelid = t.oid AND a.attnum = ANY(i.indkey)
LEFT JOIN pg_class c ON c.oid = i.indexrelid
WHERE t.relkind = 'r'
  AND c.relname IS NULL
  AND a.attnum > 0
  AND NOT a.attisdropped
ORDER BY t.relname;
```

---

## Schéma de base de données — référence d'implémentation

Cette section décrit le schéma **actuellement implémenté** dans `app.py`. Elle fait autorité pour les opérations courantes ; les champs et relations présentés ailleurs comme évolutions futures ne doivent pas être supposés présents en base.

### Moteurs et initialisation

| Environnement | Moteur | Initialisation |
|---------------|--------|----------------|
| Production | PostgreSQL 15+ via `DATABASE_URL` ou `DB_USER`/`DB_PASSWORD` | `Base.metadata.create_all()` au démarrage |
| Tests | SQLite en mémoire avec `TESTING=1` | `Base.metadata.create_all()` puis `drop_all()` dans les fixtures |
| Développement Docker | PostgreSQL 15, base `music_hall` | script d'initialisation monté dans `compose.yaml` |

`create_all()` crée les tables absentes, mais n'altère pas les colonnes existantes. Un changement de type, de contrainte ou de nom de colonne nécessite donc une migration explicite et une sauvegarde préalable.

### Diagramme logique actuel

```text
+---------------------------+       +---------------------------+
| users                     |       | logs                      |
|---------------------------|       |---------------------------|
| id PK                     |       | id PK                     |
| username UNIQUE NOT NULL  |       | level NOT NULL            |
| email UNIQUE NOT NULL     |       | message TEXT NOT NULL     |
| password_hash NOT NULL    |       | source                    |
| is_active DEFAULT true    |       | created_at                |
| created_at                |       +---------------------------+
+---------------------------+

+---------------------------+
| analyses                  |
|---------------------------|
| id PK                     |
| type NOT NULL             |
| input_data                |
| result                    |
| created_at                |
+---------------------------+
```

Aucune clé étrangère ni relation SQLAlchemy n'est actuellement déclarée entre ces trois tables. Le champ `log_id` renvoyé par `POST /logs/{log_id}/analyze` est une valeur de réponse ; il n'est pas persisté dans `analyses`.

### Table `users`

| Colonne | Type SQLAlchemy | Nullable | Contrainte / valeur par défaut | Usage |
|---------|-----------------|----------|--------------------------------|-------|
| `id` | `Integer` | Non | clé primaire, auto-incrémentée | identifiant interne |
| `username` | `String(50)` | Non | index unique | connexion et affichage |
| `email` | `String(120)` | Non | index unique | récupération et contact |
| `password_hash` | `String(256)` | Non | bcrypt, coût 12 | authentification ; aucun mot de passe clair |
| `is_active` | `Boolean` | Oui | `True` | désactivation logique des comptes |
| `created_at` | `DateTime` | Oui | `datetime.utcnow` | date de création |

Indexes déclarés :

- `ix_users_username` : unicité de `username`.
- `ix_users_email` : unicité de `email`.

La création d'un utilisateur est validée par `UserCreate` : nom de 3 à 50 caractères, email valide et mot de passe d'au moins 8 caractères. La suppression par l'API positionne `is_active` à `False` ; elle ne supprime pas la ligne.

### Table `logs`

| Colonne | Type SQLAlchemy | Nullable | Contrainte / valeur par défaut | Usage |
|---------|-----------------|----------|--------------------------------|-------|
| `id` | `Integer` | Non | clé primaire, auto-incrémentée | identifiant du log |
| `level` | `String(20)` | Non | — | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `message` | `Text` | Non | longueur applicative maximale : 4096 | contenu ingéré |
| `source` | `String(100)` | Oui | valeur applicative par défaut : `unknown` | origine du log |
| `created_at` | `DateTime` | Oui | `datetime.utcnow` | date d'ingestion |

Indexes déclarés :

- `ix_logs_level`
- `ix_logs_source`
- `ix_logs_created_at`
- `ix_logs_level_created_at`
- `ix_logs_source_created_at`
- `ix_logs_level_source_created_at`

Les validations de niveau, de longueur et de source sont appliquées avant insertion par Pydantic et par les endpoints bulk/CSV. Le modèle ne contient pas de colonne `log_metadata` ni de colonne `user_id` dans l'implémentation actuelle.

### Table `analyses`

| Colonne | Type SQLAlchemy | Nullable | Contrainte / valeur par défaut | Usage |
|---------|-----------------|----------|--------------------------------|-------|
| `id` | `Integer` | Non | clé primaire, auto-incrémentée | identifiant de l'analyse |
| `type` | `String(50)` | Non | — | type d'analyse, par exemple `log_analysis` |
| `input_data` | `Text` | Oui | — | donnée d'entrée conservée |
| `result` | `Text` | Oui | — | résultat JSON sérialisé du provider |
| `created_at` | `DateTime` | Oui | `datetime.utcnow` | date de création |

`POST /logs/{log_id}/analyze` vérifie d'abord que le log existe, appelle le provider, puis insère une ligne dans `analyses`. La réponse contient `log_id`, mais la table ne possède pas de colonne correspondante. `POST /analyses` accepte un objet contenant au moins `type` et conserve éventuellement `input_data` et `result`.

Le contenu de `result` suit le contrat `AnalysisResult` : `severity`, `category`, `summary`, `recommendations` et `provider`. Il doit être traité comme du JSON stocké dans du texte, et non comme une colonne JSON typée.

### Relations, requêtes et rétention

- La relation `logs` ? `analyses` est **logique et applicative**, pas référentielle en base.
- Les utilisateurs et les logs sont indépendants ; aucune attribution d'auteur n'est persistée.
- Les listes sont triées par `created_at DESC` dans les endpoints de lecture.
- `CleanupService` supprime les logs et analyses antérieurs à un seuil configurable, par défaut 90 jours. Les utilisateurs ne sont pas supprimés automatiquement par ce service.
- Les exports et rapports lisent les tables via SQLAlchemy ; ils ne doivent pas contourner les validations d'entrée de l'API.

Exemples d'inspection :

```bash
# PostgreSQL Docker
docker compose exec db psql -U "$(cat secrets/postgres_user.txt)" -d music_hall -c "\\d+ users"
docker compose exec db psql -U "$(cat secrets/postgres_user.txt)" -d music_hall -c "\\d+ logs"
docker compose exec db psql -U "$(cat secrets/postgres_user.txt)" -d music_hall -c "\\d+ analyses"

# Volumes et cardinalités
docker compose exec db psql -U "$(cat secrets/postgres_user.txt)" -d music_hall -c \
  "SELECT 'users' AS table_name, count(*) FROM users
   UNION ALL SELECT 'logs', count(*) FROM logs
   UNION ALL SELECT 'analyses', count(*) FROM analyses;"
```

### Évolution du schéma

Pour toute modification :

1. Sauvegarder la base et valider la restauration dans un environnement isolé.
2. Ajouter ou modifier les modèles SQLAlchemy et les schémas Pydantic associés.
3. Écrire une migration PostgreSQL explicite pour les changements destructifs ou incompatibles.
4. Mettre à jour les tests d'intégration, les exports, les requêtes d'administration et la présente référence.
5. Déployer la migration avant la version applicative qui dépend de la nouvelle colonne.
6. Vérifier les indexes, les contraintes, les performances et la rétention après déploiement.

Évolutions à ne pas considérer comme disponibles aujourd'hui : `role` sur `users`, `log_metadata` sur `logs`, `user_id` sur `logs`, clé étrangère `analyses.log_id`, partitionnement mensuel et recherche full-text.

---

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

## Observabilité et monitoring

Cette stack est optionnelle en développement et recommandée en production. Elle sépare les signaux sans centraliser les secrets ou les logs sensibles dans les tableaux de bord.

```text
Client / healthcheck
        |
        v
+----------------+       +----------------+       +----------------+
| Prometheus     |<------| API FastAPI    |------>| Loki           |
| métriques      |       | /metrics       |       | logs structurés|
+-------+--------+       +----------------+       +-------+--------+
        |                                               |
        v                                               v
+----------------+       +----------------+       +----------------+
| Grafana        |<------| Jaeger         |<------| traces OpenTelemetry |
| dashboards     |       | UI / stockage  |       | (quand activé)    |
+----------------+       +----------------+       +----------------+
```

### Prérequis et ports

- Docker Engine et Docker Compose v2.
- L'API doit être joignable sur le réseau Docker et exposer `/health` et `/metrics`.
- Les ports ci-dessous sont des ports locaux de consultation ; en production, publiez uniquement Grafana et Jaeger derrière un reverse proxy authentifié.

| Composant | Port local | Usage |
|-----------|------------|-------|
| API | `5000` | `/health`, `/metrics` |
| Prometheus | `9090` | collecte et requêtes PromQL |
| Grafana | `3000` | dashboards et alertes |
| Loki | `3100` | requêtes LogQL |
| Jaeger | `16686` | recherche de traces |
| Jaeger OTLP/UDP | `4317`, `6831` | réception des traces |

### Lancer la stack locale

Les commandes suivantes utilisent des conteneurs autonomes afin de rester indépendantes du fichier Compose de l'application. Adaptez les versions et le réseau à votre environnement.

```bash
# Réseau partagé avec le service web de Log Sentinel API
docker network create log-sentinel-observability 2>/dev/null || true

# Prometheus (le fichier de configuration est décrit ci-dessous)
docker run -d --name log-sentinel-prometheus \
  --network log-sentinel-observability \
  -p 9090:9090 \
  -v "$PWD/config/prometheus.yml:/etc/prometheus/prometheus.yml:ro" \
  prom/prometheus:v2.48.0

# Loki
docker run -d --name log-sentinel-loki \
  --network log-sentinel-observability \
  -p 3100:3100 \
  grafana/loki:2.9.8

# Jaeger all-in-one
docker run -d --name log-sentinel-jaeger \
  --network log-sentinel-observability \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 16686:16686 \
  -p 4317:4317 \
  -p 6831:6831/udp \
  jaegertracing/all-in-one:1.53.0

# Grafana (mot de passe à changer avant toute exposition réseau)
docker run -d --name log-sentinel-grafana \
  --network log-sentinel-observability \
  -p 3000:3000 \
  -e GF_SECURITY_ADMIN_USER=admin \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana:10.2.2
```

Pour une stack Compose, ajoutez les services à un fichier d'overlay dédié et lancez :

```bash
docker compose -f compose.yaml -f docker-compose.observability.yml up -d
docker compose -f compose.yaml -f docker-compose.observability.yml ps
```

### Configuration Prometheus

Créez `config/prometheus.yml` avec une cible correspondant au nom de service de l'API. Avec `compose.yaml`, la cible est généralement `web:5000` ; avec les conteneurs autonomes, connectez le service API au réseau ou utilisez `host.docker.internal:5000` selon la plateforme.

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: log-sentinel-api
    metrics_path: /metrics
    static_configs:
      - targets: ["web:5000"]
```

Vérifiez la collecte :

```bash
curl -fsS http://localhost:9090/-/ready
curl -fsS 'http://localhost:9090/api/v1/targets' | python -m json.tool
curl -fsS http://localhost:5000/health
curl -fsS http://localhost:5000/metrics
```

Si `/metrics` répond `404`, vérifiez que l'image déployée active l'instrumentation Prometheus ; `/health` reste le contrôle de disponibilité minimal.

### Configuration Grafana

1. Ouvrez `http://localhost:3000` et authentifiez-vous.
2. Ajoutez Prometheus : **Connections ? Data sources ? Prometheus**, URL `http://log-sentinel-prometheus:9090`.
3. Ajoutez Loki : URL `http://log-sentinel-loki:3100`.
4. Ajoutez Jaeger : URL `http://log-sentinel-jaeger:16686`.
5. Importez les dashboards décrits ci-dessous ou utilisez l'import JSON de Grafana.

Dashboards recommandés :

| Dashboard | Panneaux minimum | Requêtes / sources |
|-----------|------------------|--------------------|
| **Log Sentinel API — Vue générale** | requêtes/s, taux d'erreur, p50/p95/p99, santé DB, logs ingérés, analyses produites | `rate(http_requests_total[5m])`, `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`, `/metrics` |
| **Ingestion et qualité des logs** | volume par niveau et source, rejets bulk/CSV, taille des payloads, logs sans analyse | labels `level`, `source`, `status`, `endpoint` ; Loki + Prometheus |
| **Sécurité et limites** | 401/403/429, tentatives par IP, rate-limit, événements de redaction, accès admin | `rate(http_requests_total{status=~"401|403|429"}[5m])`, LogQL sur les logs d'audit |
| **Base de données** | connexions actives/idle, requêtes lentes, taille des tables, échecs healthcheck | métriques PostgreSQL/exporter et `/health` |
| **Traces et providers LLM** | durée par route, traces par provider, erreurs/timeout, fallback fake | Jaeger service `log-sentinel-api`, spans `db`, `llm`, `http` |

Exemples de requêtes PromQL à copier dans Grafana :

```promql
# Taux d'erreurs HTTP sur 5 minutes
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))

# Latence p95 par endpoint
histogram_quantile(
  0.95,
  sum by (le, endpoint) (rate(http_request_duration_seconds_bucket[5m]))
)

# Requêtes par minute et statut
sum by (status) (rate(http_requests_total[5m])) * 60

# Logs ingérés et analyses créées
rate(log_sentinel_logs_created_total[5m])
rate(log_sentinel_analyses_created_total[5m])

# Provider LLM en erreur
sum by (provider) (rate(llm_provider_errors_total[5m]))
```

### Logs avec Loki

L'application doit émettre des logs structurés JSON avec, au minimum, `timestamp`, `level`, `message`, `request_id`, `route`, `source` et `duration_ms`. Les champs contenant des credentials, tokens, clés API ou données personnelles doivent être redactés avant l'envoi.

Exemples LogQL :

```logql
# Tous les logs de l'API
{job="log-sentinel-api"}

# Erreurs et critiques des 15 dernières minutes
{job="log-sentinel-api"} |= "ERROR" | duration_ms > 500

# Requets avec un request_id connu
{job="log-sentinel-api"} |= "request_id" | line_format "{{.request_id}} {{.message}}"

# Recherche d'une éventuelle donnée sensible (à traiter comme alerte, pas comme affichage)
{job="log-sentinel-api"} |~ "(?i)(password|token|api[_-]?key|authorization)"
```

Pour acheminer les logs Docker vers Loki, utilisez Promtail ou Alloy avec un job `docker` qui ajoute le label `job="log-sentinel-api"` et filtre les conteneurs `web`. Ne montez pas le socket Docker en production sans restreindre les permissions.

### Traces avec Jaeger

Lorsque l'instrumentation OpenTelemetry est activée, configurez l'exporteur vers `log-sentinel-jaeger:4317` (OTLP) ou `log-sentinel-jaeger:6831` (Jaeger Thrift UDP) et utilisez le nom de service `log-sentinel-api`. Propagez le `request_id` en en-tête et ajoutez des spans pour :

- la réception HTTP et le code de statut ;
- l'ingestion JSON/CSV et le nombre de lignes acceptées/rejetées ;
- les appels PostgreSQL ;
- l'appel au provider LLM, sans envoyer le contenu sensible du prompt ;
- les fallback et timeouts.

Consultez les traces dans `http://localhost:16686`, recherchez par `request_id`, endpoint, statut HTTP ou provider, puis corrèlez le trace ID avec les logs Grafana/Loki.

### Alertes de base

Importez ou adaptez ces règles Prometheus :

```yaml
groups:
  - name: log-sentinel-slo
    rules:
      - alert: LogSentinelHighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          / sum(rate(http_requests_total[5m])) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Taux d'erreurs API supérieur à 5 %"

      - alert: LogSentinelDatabaseDown
        expr: up{job="log-sentinel-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "API ou cible de santé indisponible"

      - alert: LogSentinelHighLatency
        expr: |
          histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
          > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Latence p95 supérieure à 500 ms"
```

### Arrêt et hygiène

```bash
docker stop log-sentinel-grafana log-sentinel-prometheus log-sentinel-loki log-sentinel-jaeger
docker rm log-sentinel-grafana log-sentinel-prometheus log-sentinel-loki log-sentinel-jaeger
```

En production, activez TLS, l'authentification Grafana, la rétention adaptée, le chiffrement des données de télémétrie et une allowlist réseau. Ne publiez pas Prometheus, Loki ou Jaeger directement sur Internet.

---

## Contribuer