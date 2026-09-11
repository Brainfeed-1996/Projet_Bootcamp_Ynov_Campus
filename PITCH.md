# PITCH — Log Sentinel API

**Log Sentinel API** — *Ingestion et analyse de logs sécurisée, par les DevSecOps, pour les DevSecOps.*

---

## 1. Problème

Les équipes defensive ops génèrent des volumes massifs de logs (application, infra, sécurité) mais disposent d'aucun canal fiable, **sécurisé by design**, pour les ingérer, les centraliser et les analyser rapidement — sans fuiter de secrets, sans dépendre d'un LLM externe en permanence, sans vulnérabilités d'image ou de pipeline CI. Résultat : visibilité opérationnelle limitée, fuite de données sensibles, et posture de sécurité inégèbre.

---

## 2. Solution

Log Sentinel est une **API FastAPI** d'ingestion et d'analyse de logs qui combine :

- **Ingestion** JSON / CSV avec validation Pydantic stricte (niveaux, longueurs, emails).
- **Analyse IA** via un fournisseur LLM **pluggable** (OpenAI, Ollama, ou `Fake` offline 100 % déterministe).
- **Sécurité conteneur** : image `python:3.11-slim`, user non-root (UID 1000), filesystem `read_only`, `cap_drop ALL`, `no-new-privileges`, healthcheck intégré.
- **Gestion des secrets** : `.env` dev, **Docker Secrets** (`/run/secrets/`, chmod 400) prod, Vault en option (agent sidecar).
- **CI/CD qualité** : Trivy (SARIF → GitHub Security) + Snyk (deps + code) ; build bloquant si CVE HIGH/CRITICAL.
- **Offline-ready** : `TESTING=1` → SQLite en mémoire + `FakeProvider`, **0 dépendance externe**, 16 tests en < 2 s.
- **Observabilité** : `/health` (DB up/down), logs structurés, endpoints filtrables /logs?level=...&limit=....

---

## 3. Points clés de la démo (6 min — 50/50 A/B)

| Temps | Orateur | Focus | Support |
|-------|---------|-------|---------|
| 0:00–0:35 | **A** | Pitch produit & valeur business | Slide architecture |
| 0:35–1:10 | **B** | Hardening conteneur + Trivy 0 CVE HIGH/CRIT | Dockerfile + log CI |
| 1:10–1:50 | **A** | Secrets & Config : `.env` → Docker Secrets → Vault | Terminal `init-docker-secrets.sh` |
| 1:50–2:30 | **B** | Pipeline CI : tests → build → Trivy → Snyk | `.github/workflows/ci.yml` |
| 2:30–3:10 | **A** | Live : créer un log → 201 | `curl POST /logs` |
| 3:10–3:50 | **B** | Live : analyser avec IA (FakeProvider) | `curl POST /logs/1/analyze` |
| 3:50–4:15 | **A** | Live : filtres & health | `curl GET /logs?...` + `/health` |
| 4:15–4:50 | **B** | Tests offline + Quality Gate | `pytest -v` (16 passed) |
| 4:50–5:25 | **A** | Prod & Vault : ressources, restart, sidecar | `docker-compose.production.yml` |
| 5:25–5:50 | **B** | DoD & versioning : SemVer + GitFlow | Checklist DoD |
| 5:50–6:00 | **A+B** | Closing commun | Slide contact |

---

## 4. Stack technique

Python 3.11 + FastAPI + SQLAlchemy + bcrypt — PostgreSQL (ou SQLite en test) — Docker / Compose — Trivy / Snyk — Vault optionnel — pytest.

---

## 5. Différenciateurs clés

- **DevSecOps natif** : sécurité intégrée au build (non-root, read-only, scans CI), pas un ajout ultérieur.
- **Zéro secret en dur** : secrets montés via Docker Secrets / Vault, jamais dans l'image ni le repo.
- **Résilience IA** : fournisseur `fake` garantit la démo et le service même si OpenAI/Ollama sont down.
- **Reproductible** : `git clone` → `./scripts/init-docker-secrets.sh` → `docker compose up`, DoD validée.
- **Quality gate bloquant** : tests + 0 CVE HIGH/CRIT + 0 vulnérabilité HIGH Snyk = merge autorisé.

---

## 6. Plan de démo live (3 commandes)

```bash
curl -X POST http://localhost:5000/logs -H "Content-Type: application/json" \
  -d '{"message":"DB connection timeout","level":"ERROR","source":"api-gateway"}'
curl -X POST http://localhost:5000/logs/1/analyze
curl http://localhost:5000/health
```

> Fallback testé : si l'API n'est pas containerisée, `TESTING=1 LLM_PROVIDER=fake uvicorn app:app --port 5000`.

---

## 7. Ce que le jury doit retenir

- **Log Sentinel** = ingestion + analyse de logs **sécurisée by design**, pas seulement "avec sécurité".
- **DevSecOps opérationnel** : image durcie, secrets isolés, pipeline CI bloquant — le code ne merge que s'il est sain.
- **Démo live fiable** : 3 commandes, résultat immédiat, plan de secours sans IA ni Docker validé.
- **Prêt production** : ressources limitées, restart policy, healthcheck, SemVer + GitFlow, DoD complète.

> Repo : `Log Sentinel API` — `v1.0.0` — questions ?
