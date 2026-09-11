# DEMO DAY — Music Hall (6 min, 50/50)

**Objectif** : Démontrer une app DevSecOps complète (logs + IA) en 6 min chrono.  
**Rôles** : **Orateur A** (Produit / Démo live) — **Orateur B** (Tech / Sécurité / CI)  
**Répartition** : 50 % temps de parole chacun (3 min / 3 min).  
**Public** : Jury technique + métier.  
**Prérequis** : Stack démarrée (`docker compose up -d`), terminal prêt, navigateur/curl.

---

## Timing précis (360 s)

| Temps | Durée | Orateur | Action / Parole clé | Support |
|-------|-------|---------|---------------------|---------|
| 0:00–0:30 | 30 s | **A** | **Intro** : « Music Hall — service d’ingestion et d’analyse de logs sécurisé. Flask + PostgreSQL + LLM (OpenAI/Ollama/Fake). DevSecOps natif : secrets, scans, CI. » | Écran titre + architecture (1 slide) |
| 0:30–1:10 | 40 s | **B** | **Architecture & Sécurité conteneur** : « Base python:3.11-slim, user non-root, read-only fs, cap_drop ALL, Trivy intégré au build. 0 CVE HIGH/CRITICAL. » | `Dockerfile` (lignes 15–27) + Trivy log CI |
| 1:10–1:50 | 40 s | **A** | **Secrets & Config** : « Aucun secret en dur. .env pour dev, Docker Secrets (fichiers chmod 400) pour prod, Vault optionnel. Démo : `./scripts/init-docker-secrets.sh` génère 4 secrets. » | Terminal : script + `ls -la secrets/` |
| 1:50–2:30 | 40 s | **B** | **CI Pipeline** : « GitHub Actions : tests → build → Trivy (SARIF → GitHub Security) → Snyk deps + code. Échec si HIGH+. Secrets CI : SNYK_TOKEN. » | `.github/workflows/ci.yml` (30 lignes) |
| 2:30–3:10 | 40 s | **A** | **Démo live — Créer un log** : `curl -X POST /logs -d '{"message":"DB connection timeout","level":"ERROR","source":"api"}'` → 201. | Terminal curl + réponse JSON |
| 3:10–3:50 | 40 s | **B** | **Démo live — Analyser avec IA (FakeProvider)** : `curl -X POST /logs/1/analyze` → severity LOW, category TEST, summary, recommendations. « Provider pluggable : `LLM_PROVIDER=fake|ollama|openai`. » | Terminal curl + JSON résultat |
| 3:50–4:20 | 30 s | **A** | **Démo live — Filtres & Health** : `GET /logs?level=ERROR&limit=5` + `GET /health` → `{"status":"ok","database":"up"}`. | Terminal |
| 4:20–4:50 | 30 s | **B** | **Tests offline & Quality Gate** : « `TESTING=1` → SQLite mémoire, FakeProvider, 0 dépendance externe. `pytest -v` : 4 tests passent en <2 s. Quality gate : tests + Trivy + Snyk. » | `pytest -v` output |
| 4:50–5:20 | 30 s | **A** | **Prod & Vault** : « `docker-compose.production.yml` : secrets montés, ressources limitées, restart policy. Vault optionnel : agent sidecar, rotation centralisée. » | `docker-compose.production.yml` (extrait) |
| 5:20–5:50 | 30 s | **B** | **DoD & Versioning** : « DoD : tests + Trivy 0 HIGH/CRIT + Snyk 0 HIGH + secrets OK + health check + rollback testé. SemVer + GitFlow : main=prod, develop=CI, tags vX.Y.Z. » | Checklist DoD (slide) |
| 5:50–6:00 | 10 s | **A+B** | **Closing** (ensemble) : « Music Hall — prêt production, sécurisé by design, observable, extensible. Questions ? » | Slide contact / QR repo |

---

## Plan de secours (Sans IA / Dégradé)

| Scénario | Déclencheur | Action immédiate | Message au jury |
|----------|-------------|------------------|-----------------|
| **LLM indisponible** (Ollama/OpenAI down, timeout, quota) | `/logs/1/analyze` → 502 ou >5 s | Basculer `LLM_PROVIDER=fake` (reload auto ou restart web) : `docker compose restart web` | « L’IA est un service externe ; le fallback `fake` garantit la démo et la résilience prod. » |
| **DB down** | `/health` → `database: down` | Vérifier `docker compose logs db` ; `docker compose restart db` | « Health check + restart policy = auto-healing. » |
| **Build Trivy fail** (CVE critique sur base image) | CI rouge | Montrer `.trivyignore` justifié ou `docker pull python:3.11-slim` récent | « Scan bloquant = garde-fou. Exception documentée = traçabilité. » |
| **Secrets manquants** | Conteneur web crash au démarrage | `./scripts/init-docker-secrets.sh` + `docker compose up -d` | « Secrets générés à la volée en dev ; en prod = Vault. » |
| **Réseau / Port occupé** | `port 5000 already in use` | `docker compose down` + changer port dans `compose.yaml` (ex: 5001:5000) | « Config externalisée, pas de code modifié. » |
| **Démo curl échoue** (typos, JSON invalide) | Erreur 400/500 | Avoir les commandes **pré-copiées** dans un fichier `demo-commands.sh` | « Script de démo versionné = reproductible. » |

**Fichier `demo-commands.sh` (à créer localement, non commit) :**
```bash
#!/bin/bash
# Commandes de démo pré-testées
curl -X POST http://localhost:5000/users -H "Content-Type: application/json" -d '{"username":"demo","email":"demo@test.com","password":"Demo123!"}'
curl -X POST http://localhost:5000/logs -H "Content-Type: application/json" -d '{"message":"DB connection timeout","level":"ERROR","source":"api-gateway"}'
curl -X POST http://localhost:5000/logs/1/analyze
curl "http://localhost:5000/logs?level=ERROR&limit=5"
curl http://localhost:5000/health
curl -X GET http://localhost:5000/analyses
```

---

## Critères de réussite (Definition of Demo Success)

| Critère | Validé si |
|---------|-----------|
| **Temps respecté** | ≤ 6:00 (chronométré) |
| **Parité 50/50** | A ≈ 180 s, B ≈ 180 s (±10 s) |
| **Démo live OK** | 3 endpoints répondent (créer log, analyser, health) |
| **Pas de "uh/eh"** | Fluidité, transitions préparées |
| **Sécurité visible** | Trivy, secrets, read-only, non-root mentionnés |
| **CI visible** | Workflow + résultats (SARIF, Snyk) montrés |
| **Fallback prouvé** | Bascule `fake` expliquée (même si non déclenchée) |
| **Closing net** | Dernière phrase commune, ouvre aux questions |

---

## Répartition 50/50 — Résumé par orateur

### Orateur A — Produit & Démo (3 min)
| Segment | Temps | Contenu clé |
|---------|-------|-------------|
| Intro | 0:30 | Pitch produit + valeur |
| Secrets/Config | 0:40 | .env → Docker Secrets → Vault |
| Live: Créer log | 0:40 | `POST /logs` |
| Live: Analyser (Fake) | 0:40 | `POST /logs/1/analyze` |
| Live: Filtres + Health | 0:30 | `GET /logs?...` + `/health` |
| Prod & Vault | 0:30 | production.yml + Vault sidecar |
| Closing | 0:10 | Call to action |
| **Total** | **3:00** | |

### Orateur B — Tech & Sécurité (3 min)
| Segment | Temps | Contenu clé |
|---------|-------|-------------|
| Arché + Sécurité conteneur | 0:40 | Dockerfile hardening, Trivy build |
| CI Pipeline | 0:40 | Tests → Build → Trivy → Snyk |
| Tests offline + Quality Gate | 0:30 | `TESTING=1`, FakeProvider, pytest |
| DoD + Versioning | 0:30 | Checklist + SemVer/GitFlow |
| Closing (avec A) | 0:10 | Ensemble |
| **Total** | **3:00** | |

---

## Check-liste pré-démo (J-1 / H-1)

- [ ] `docker compose up -d --build` : tout vert (web + db healthy)
- [ ] `curl /health` → `{"status":"ok","database":"up"}`
- [ ] `curl POST /logs` → 201, `POST /logs/1/analyze` → 201 (FakeProvider)
- [ ] `pytest -v` : 4 passed en <3 s
- [ ] `docker compose -f compose.yaml -f docker-compose.production.yml config` : valide
- [ ] `trivy image music-hall:latest` : 0 HIGH/CRITICAL
- [ ] Slides/écrans prêts : architecture, Dockerfile, CI, DoD, versioning
- [ ] `demo-commands.sh` testé, ouvert dans terminal
- [ ] Chronomètre visible (téléphone / second écran)
- [ ] Bascule `LLM_PROVIDER=fake` confirmée dans `.env` ou `compose.yaml`
- [ ] Plan de secours lu par les deux orateurs

---

## Notes de présentation

- **Ne pas lire** : parler à l'écran, pointer du doigt (terminal, code, slides).
- **Montrer le code** : 10-15 s max par fichier (lignes clés seulement).
- **Terminal > Slides** : le live prime, les slides sont du contexte.
- **Silence = confiance** : ne pas combler les latences curl par du bruit.
- **Si question technique** : B répond ; si métier : A répond. Court, factuel.
- **Finir à l'heure** : couper le superflu, garder le closing commun.