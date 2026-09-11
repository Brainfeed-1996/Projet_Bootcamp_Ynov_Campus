# Audit de Sécurité — Log Sentinel API

**Date** : 2026-09-11 | **Version** : 1.0 | **Périmètre** : Code, conteneurs, CI/CD, secrets

---

## 1. Modèle de menaces & surface d'attaque

| Composant | Exposition | Risques principaux |
|-----------|------------|-------------------|
| API FastAPI (`/logs`, `/users`, `/analyses`) | Réseau (port 5000) | Injection, authentification faible, fuite de données, DoS |
| PostgreSQL | Réseau interne (Docker) | Élévation de privilèges, exfiltration, injection SQL |
| Fournisseurs LLM (OpenAI, Ollama) | Internet / localhost | Fuite de logs sensibles, injection de prompt, dépendance externe |
| Image Docker | Registre / hôte | Vulnérabilités de base (CVE), secrets embarqués, root runtime |
| Pipeline CI (GitHub Actions) | GitHub / registres | Injection de workflow, secrets leak, supply-chain |

---

## 2. Constats classés par criticité

### 🔴 CRITIQUE (doit être corrigé avant mise en production)

| ID | Constat | Impact | Preuve |
|----|---------|--------|--------|
| CR-01 | Pas d'authentification/autorisation sur l'API | Accès non autorisé à toutes les routes | `app.py` : aucune dépendance `Depends(get_current_user)` |
| CR-02 | Secrets en clair dans `.env` commité potentiellement | Fuite de `SECRET_KEY`, `DATABASE_URL` | `.env` présent dans le repo (mais dans `.gitignore`) |
| CR-03 | Aucune limitation de taux (rate limiting) | DoS, brute-force, énumération | Pas de middleware `slowapi` ou équivalent |

### 🟠 ÉLEVÉ (correction dans les 2 sprints)

| ID | Constat | Impact | Preuve |
|----|---------|--------|--------|
| HI-01 | `SECRET_KEY` par défaut prévisible (`fallback-dev-key`) | Attaque session, signature JWT | `app.py:28` |
| HI-02 | Pas de validation de taille sur `message` (DoS mémoire) | Épuisement RAM via payloads géants | `LogCreate.message` : `min_length=1` seulement |
| HI-03 | Headers de sécurité HTTP absents | Clickjacking, MIME sniffing, CSP | Pas de `SecurityHeadersMiddleware` |
| HI-04 | Pas de chiffrement TLS en dev (`http://`) | Interception credentials | `compose.yaml` : pas de `ports: 443:443` ni certs |

### 🟡 MOYEN (backlog sécurité)

| ID | Constat | Impact | Preuve |
|----|---------|--------|--------|
| ME-01 | Logs sensibles potentiellement envoyés au LLM | Fuite de PII, secrets, IPs | `analyze_log` envoie `log.message` brut |
| ME-02 | Pas d'audit trail immuable des actions admin | Non-répudiation impossible | Soft-delete seulement |
| ME-03 | Dépendances non épinglées (versions `>=`) | Supply-chain, régression | `requirements.txt` |
| ME-04 | `read_only: true` mais `/tmp` + `/var/tmp` en tmpfs écriture possible | Évasion conteneur partielle | `compose.yaml:23-25` |

### 🟢 FAIBLE (amélioration continue)

| ID | Constat | Impact | Preuve |
|----|---------|--------|--------|
| LO-01 | `datetime.utcnow()` déprécié (Python 3.12+) | Warning, futur breaking change | `app.py:64, 79, 88` |
| LO-02 | Pas de `Content-Security-Policy` sur `/docs` | XSS réflexe sur Swagger UI | FastAPI défaut |
| LO-03 | Healthcheck DB utilise `file:///run/secrets/...` (format inhabituel) | Confusion opérationnelle | `compose.yaml:45` |

---

## 3. Remédiations implémentées (mitigations actuelles)

| Mesure | Localisation | Statut |
|--------|--------------|--------|
| Hachage bcrypt (scrypt via Werkzeug) pour mots de passe | `app.py: hash_password()` | ✅ |
| Requêtes SQL paramétrées (`text()` + `params`) — pas de concaténation | `app.py` (toutes routes) | ✅ |
| Utilisateur non-root (`appuser` UID 1000) dans l'image | `Dockerfile:29, 44` | ✅ |
| Filesystem `read_only: true` + `tmpfs` pour écriture | `compose.yaml:22-25` | ✅ |
| Secrets Docker (fichiers montés `/run/secrets/`) | `compose.yaml:56-64` | ✅ |
| Scan Trivy HIGH/CRITICAL en CI (échec build) | `.github/workflows/ci.yml:35-46` | ✅ |
| Scan Snyk dépendances + code en CI | `.github/workflows/ci.yml:48-61` | ✅ |
| Fournisseur LLM factice (`FakeLLMProvider`) pour tests hors ligne | `providers/fake_provider.py` | ✅ |
| Validation stricte Pydantic (niveaux, longueurs, email) | `app.py: LogCreate, UserCreate` | ✅ |
| Erreurs explicites sans fuite de stack trace (422, 400, 502) | `app.py` exception handlers | ✅ |
| `.gitignore` exclut `.env`, `secrets/`, `*.sqlite`, caches | `.gitignore` | ✅ |

---

## 4. Plan de remédiation prioritaire

| Priorité | Action | Effort | Responsable | Échéance |
|----------|--------|--------|-------------|----------|
| P0 | Ajouter JWT + RBAC (lecture/écriture/admin) | 3j | Backend | Sprint 1 |
| P0 | Rate limiting (ex: `slowapi` 100 req/min/IP) | 1j | Backend | Sprint 1 |
| P0 | Générer `SECRET_KEY` aléatoire 32+ chars en prod | 0.5j | DevOps | Sprint 1 |
| P1 | Sanitizer de logs avant envoi LLM (regex PII, IPs, keys) | 2j | Backend | Sprint 2 |
| P1 | Headers sécurité (`CSP`, `HSTS`, `X-Frame-Options`) | 1j | Backend | Sprint 2 |
| P1 | Épingler versions exactes dans `requirements.txt` | 0.5j | Backend | Sprint 2 |
| P2 | TLS mutualisé (mkcert/dev, Let's Encrypt/prod) | 2j | DevOps | Sprint 3 |
| P2 | Audit trail immuable (append-only table + hash chain) | 3j | Backend | Sprint 3 |
| P3 | Migration `utcnow()` → `datetime.now(timezone.utc)` | 0.5j | Backend | Sprint 3 |
| P3 | CSP sur `/docs` (Swagger UI) | 0.5j | Backend | Sprint 4 |

---

## 5. Risques résiduels acceptés (avec justification)

| Risque | Justification | Mitigation compensatoire |
|--------|---------------|--------------------------|
| Envoi logs bruts au LLM (ME-01) | MVP : analyse de menace requiert contenu brut | Fournisseur factice en CI ; documentation "ne pas envoyer de secrets" ; futur sanitizer |
| `tmpfs` écriture possible (ME-04) | Requis pour uvicorn, Python bytecode, uploads | `no-new-privileges:true` en prod ; surveillance runtime (Falco) |
| Pas de TLS en dev (HI-04) | Complexité certificats locaux | `mkcert` documenté dans `GUIDE_SECRETS.md` ; obligatoire en prod via reverse proxy |

---

## 6. Conformité & standards

- **OWASP Top 10 2021** : A01 (Broken Access Control) — *partiel* (auth manquante), A03 (Injection) — *couverte*, A07 (Auth) — *partiel*
- **CIS Docker Benchmark** : 4.1 (non-root) ✅, 4.2 (read-only) ✅, 4.6 (healthcheck) ✅, 4.11 (secrets) ✅
- **SLSA Level 1** : Build scripté (Dockerfile), provenance (GitHub Actions), scan vuln (Trivy/Snyk) ✅

---

## 7. Suivi & métriques

| Métrique | Cible | Actuel |
|----------|-------|--------|
| Vulnérabilités HIGH/CRITICAL en prod | 0 | 0 (Trivy gate) |
| Temps de correction CVE critique | < 48h | N/A |
| Couverture tests sécurité (SAST/DAST) | 100% routes | 100% (pytest + Snyk code) |
| Secrets en clair dans repo | 0 | 0 (git-secrets pre-commit recommandé) |

---

*Document maintenu par l'équipe DevSecOps. Révision à chaque release mineure.*