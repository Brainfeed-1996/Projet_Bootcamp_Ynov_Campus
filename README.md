# Log Sentinel API

API **FastAPI** d'ingestion et d'analyse de logs sécurisée, conçue pour un cours **DevSecOps** (Ynov — Défensive).

**Version** : `v1.0.0`  
**Stack** : Python 3.11+, FastAPI, PostgreSQL, Docker, Docker Compose, Trivy, Vault (optionnel).

---

## Table des matières

1. [Prérequis](#prérequis)
2. [Tests automatisés sans IA réelle](#tests-automatisés-sans-ia-réelle)
3. [Démarrage rapide](#démarrage-rapide)
4. [Sécurité et secrets](#sécurité-et-secrets)
5. [Endpoints](#endpoints)
6. [CI/CD et scan](#cicd-et-scan)
7. [Démo Demo Day](#démo-demo-day)
8. [Définition of Done](#définition-of-done)
9. [Support et nettoyage](#support-et-nettoyage)

---

## Prérequis

- Python 3.11+ et `pip`
- Docker et Docker Compose (pour le conteneurisé)
- Git

Variables d'environnement locales : copiez `.env.production.example` en `.env.production` et adaptez les secrets si vous lancez la production hors Docker.

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

## CI/CD et scan

- `.github/workflows/ci.yml` : tests, build Docker, Trivy, Snyk.
- `Dockerfile` : image non-root `appuser` (UID 1000), build reproductible.
- `compose.yaml` : secrets Docker, `read_only`, tmpfs, limites et `cap_drop ALL` en production.
- Le scan Trivy est exécuté dans le pipeline CI, pas dans l'image de build.

---

## Démo Demo Day

Consultez `DEMO.md` pour le support de démonstration :

- Durée : **6 minutes** de démo + Q&A.
- Répartition du temps de parole : **50/50** entre Presenter A et Presenter B.
- Plan minute par minute avec commandes et résultats attendus.
- Plan de secours sans IA et sans Docker.

---

## Définition of Done

- [x] Projet repart sur une machine propre avec `git clone`, `./scripts/init-docker-secrets.sh`, `docker compose up`.
- [x] Tests automatisés passent sans accès à une vraie IA ni à PostgreSQL.
- [x] Jeu de démonstration tient en six minutes et la parole est répartie à 50/50.
- [x] Code versionné et tagué `v1.0.0`.
- [x] Documentation finale et support Demo Day fournis.
- [x] Secrets exclus de Git et de l'image Docker.
- [x] Fournisseurs IA validés sans réseau et avec erreurs explicites.

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
