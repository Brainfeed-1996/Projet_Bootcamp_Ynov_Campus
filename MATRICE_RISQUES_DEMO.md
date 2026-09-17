# Matrice des Risques — Demo Day (6 min)

| # | Commande / Étape susceptible d'échouer | Cause probable (vérifiée dans le code) | Détection (comment le voir avant/pendant) | Contournement immédiat | Phrase à dire au jury |
|---|---|---|---|---|---|
| **Docker build/up** |
| 1 | `docker compose up --build -d` | Secrets manquants : `./secrets/*.txt` absents (compose.yaml:65-73, docker-compose.production.yml:84-92) | `docker compose config` échoue ; logs `web` : "no such file" | Lancer `./scripts/init-docker-secrets.sh` avant (génère les 4 fichiers) | *"Les secrets Docker sont générés localement par script ; en prod ils viennent de Vault."* |
| 2 | `docker compose up --build -d` | Port 5000 déjà occupé (compose.yaml:10, docker-compose.production.yml:18) | `docker compose ps` montre `web` en restart loop ; `netstat -ano \| findstr :5000` | `docker compose down` puis relancer ; ou changer port dans compose.yaml | *"Le port 5000 est mappé en dev ; en prod on expose sur 80 via reverse proxy."* |
| 3 | `docker compose up --build -d` | Healthcheck DB échoue (compose.yaml:53-57, docker-compose.production.yml:69-73) : `pg_isready` attend `postgres_user` secret | `docker compose ps` → `db` reste `starting` ; `docker compose logs db` | Vérifier `secrets/postgres_user.txt` existe et correspond à `POSTGRES_USER_FILE` | *"Le healthcheck valide que Postgres accepte les connexions avec l'utilisateur secret."* |
| 4 | `docker compose -f compose.yaml -f docker-compose.production.yml up -d` | `read_only: true` + `tmpfs` manquant pour `/app/.flask` (Dockerfile:19 COPY . . écrit dans /app) | Container `web` crash au démarrage ; `dmesg \| grep -i read` | `tmpfs: - /app/.flask` déjà dans prod (docker-compose.production.yml:40) ; en dev ajouter si besoin | *"Filesystem read-only force l'écriture vers tmpfs — surface d'attaque réduite."* |
| **Health / Endpoints** |
| 5 | `curl -s http://localhost:5000/health` → 503 | DB non prête : `wait_for_db` max 30×2s (app.py:72-83) ; `DATABASE_URL` mal formé | `docker compose logs web` montre "DB not ready" ; `/health` renvoie `{"database":"down"}` | Attendre ~60s ; ou `TESTING=1` pour SQLite mémoire (conftest.py:1-2) | *"Le healthcheck attend la DB — c'est du shift-right : on expose l'état réel."* |
| 6 | `curl -s http://localhost:5000/users/1` → 404 | ID n'existe pas (app.py:275-282 : `db.get(User, user_id)` + `is_active`) | Créer d'abord via POST `/users` (demo minute 1:30) | Suivre l'ordre du DEMO.md : POST puis GET | *"L'API valide l'existence et l'état actif — pas de fuite d'info sur utilisateurs supprimés."* |
| **Docs / Secrets visibility** |
| 7 | `cat .env.production.example` → vide ou absent | Fichier non commit (vérifié : existe à 10 lignes) | `ls -la .env.production.example` | Fichier présent dans repo ; si absent, le recréer depuis template | *"Ce fichier exemple documente la config prod sans aucun secret."* |
| 8 | `ls -la secrets \| true` → répertoire vide | `init-docker-secrets.sh` non exécuté (scripts/init-docker-secrets.sh:22-30) | `docker compose config` échoue sur secrets | Lancer le script ; il génère 4 fichiers base64 32/16 chars | *"Les secrets dev sont générés localement, jamais commités (.gitignore:3)."* |
| **Base non vide / IDs** |
| 9 | `curl POST /users` → 409 "déjà existant" | Demo a déjà créé "alice" (app.py:288-293 : `SELECT ... WHERE username = :u OR email = :e`) | Réponse 409 JSON `{"detail":"Utilisateur ou email déjà existant."}` | Changer username/email dans la demo ; ou `DELETE /users/{id}` avant | *"Unicité contrainte en base + check applicatif — défense en profondeur."* |
| 10 | `curl GET /users/0` ou `/-1` → 400 | Validation `user_id <= 0` (app.py:276-277, 304-305) | Réponse 400 `"ID utilisateur invalide"` | Utiliser ID > 0 (retourné par POST) | *"Validation explicite des bornes — pas d'injection SQL possible (paramétré)."* |
| 11 | `curl POST /logs/99999/analyze` → 404 | Log ID inexistant (app.py:464-467 : `db.get(Log, log_id)`) | Réponse 404 `"Log introuvable."` | Créer le log d'abord (POST /logs) → récupérer `id` | *"Analyse liée à un log existant — traçabilité complète."* |
| **IA / LLM Provider** |
| 12 | `curl POST /logs/{id}/analyze` → 502 "Analyse IA indisponible" | Provider réel (OpenAI/Ollama) inaccessible ; timeout ou erreur réseau (app.py:468-473) | Logs `web` : "LLM analysis failed" ; `LLM_PROVIDER` != `fake` | Forcer `LLM_PROVIDER=fake` (défaut dans app.py:263) ; `.env` l'impose (ligne 2) | *"Provider `fake` par défaut — démo 100% offline, déterministe, <1s."* |
| 13 | `curl POST /logs/{id}/analyze` → 502 sur réponse LLM invalide | OpenAI/Ollama renvoie JSON mal formé / champs manquants (providers/base.py:151-198 `normalize_analysis_payload`) | Logs : "LLM response is missing required field(s)" | Provider `fake` contourne ; en prod : validation stricte côté app | *"Validation stricte du JSON LLM — schémas Pydantic, champs requis, tailles max."* |
| **Vault** |
| 14 | `docker compose -f compose.yaml -f docker-compose.vault.yml up -d` | Vault non healthy : `vault status` échoue (docker-compose.vault.yml:37-41) | `docker compose ps` → `vault` reste `starting` ; `docker compose logs vault` | Attendre ~30s ; vérifier `config/vault/config.hcl` ; `VAULT_TOKEN` requis pour `vault-agent` | *"Vault optionnel — démo montre l'architecture, pas l'instance live."* |
| 15 | `vault-agent` ne écrit pas les secrets | `VAULT_TOKEN` non défini (docker-compose.vault.yml:51) ; `kubernetes` auth non configuré | `docker compose logs vault-agent` : "permission denied" ou token manquant | Demo utilise `docker-compose.production.yml` (secrets fichiers) ; Vault = slide | *"L'agent Vault lit les secrets — jamais en dur dans l'image ni les env vars."* |
| **PowerShell (Windows)** |
| 16 | `& $curl ...` dans `test_endpoints.ps1` → "command not found" | `curl.exe` absent (Windows < 10 1803) ou alias `Invoke-WebRequest` | `$curl = "C:\Windows\System32\curl.exe"` échoue ; erreur `The term 'curl' is not recognized` | Utiliser `Invoke-RestMethod` natif PowerShell ; ou installer curl | *"Scripts fournis en .ps1 pour Windows ; `curl.exe` natif depuis Win10 1803."* |
| 17 | `docker compose ps` / `docker inspect` → noms conteneurs différents | `container_name` absent dans compose.yaml (sauf vault.yml) → noms auto `music-hall-web-1` | `docker compose ps` montre noms réels | Utiliser `docker compose ps --format "table {{.Name}}\t{{.Status}}"` | *"Noms stables via `container_name` en prod ; en dev on filtre par label/service."* |
| **Trivy / CI** |
| 18 | `trivy image music-hall:latest` → HIGH/CRITICAL | Image de base `python:3.11-slim` a CVE (ex: glibc, openssl) ; pas de `apt-get upgrade` dans Dockerfile | CI GitHub Actions (ci.yml:35-46) bloque sur `severity: HIGH,CRITICAL` | `docker build --no-cache` + `apt-get upgrade -y` dans Dockerfile avant COPY ; ou accepter risque connu | *"Trivy en CI bloque le merge sur HIGH/CRITICAL — shift-left : on fixe avant prod."* |
| 19 | `snyk test` → échoue si `SNYK_TOKEN` manquant | Secret GitHub `SNYK_TOKEN` non configuré (ci.yml:50-51, 58-59) | CI log : "SNYK_TOKEN not set" | Ajouter token dans GitHub Settings → Secrets ; ou désactiver step Snyk pour demo | *"Snyk scan double couche : deps + code — token requis, optionnel pour demo."* |
| **Tests** |
| 20 | `pytest -v` → échecs | DB state pollué entre tests (test_app.py:11-13 `reset_db()` mais pas fixture) | Tests flaky : `test_create_user_and_duplicate` passe seul, échoue après d'autres | Lancer `pytest -v --tb=short` ; chaque test appelle `reset_db()` | *"Tests isolés : SQLite mémoire, provider fake, reset DB à chaque test."* |
| 21 | `pytest` → `ModuleNotFoundError: pytest-cov` | Dépendance dev manquante (requirements.txt:15) | `pip install -r requirements.txt` puis `pytest` | `pip install pytest-cov` ou retirer `--cov` si utilisé | *"Dépendances dev séparées — image prod n'installe que requirements.txt."* |
| **Général / Fallback** |
| 22 | Conteneur ne démarre pas du tout | Docker daemon arrêté ; WSL2 non lancé (Windows) ; ressources insuffisantes | `docker version` échoue ; `docker compose up` timeout | Fallback DEMO.md:171-173 : `TESTING=1 python -m pytest -v` (offline, sans Docker) | *"Plan B : tests unitaires 100% locaux — prouvent la logique sans infra."* |
| 23 | `git status --short` → fichiers sensibles modifiés | `.env` ou `secrets/` modifiés pendant demo (app.py:36 `load_dotenv()` lit .env) | `git status` montre `.env` ou `secrets/` en modified | `.gitignore:1-3` ignore `.env`, `.env.production`, `secrets/` | *"Repo propre — aucun secret ne peut être commit accidentellement."* |

---

## Notes de vérification (sources)

- **Secrets Docker** : `compose.yaml:65-73`, `docker-compose.production.yml:84-92`, `scripts/init-docker-secrets.sh:26-30`
- **Healthcheck DB** : `compose.yaml:53-57`, `docker-compose.production.yml:69-73`, `app.py:72-83`
- **Read-only + tmpfs** : `docker-compose.production.yml:36-40`, `Dockerfile:19`
- **Validation IDs** : `app.py:276-277`, `app.py:304-305`, `app.py:462-463`, `app.py:362-363`
- **Provider fake par défaut** : `app.py:263`, `.env:2`, `conftest.py:1-2`
- **Validation LLM stricte** : `providers/base.py:151-198`, `providers/base.py:201-226`
- **Vault agent config** : `docker-compose.vault.yml:43-64`, `config/vault-agent/agent.hcl:25-42`
- **Trivy CI** : `.github/workflows/ci.yml:35-46`
- **Tests isolation** : `test_app.py:11-13`, `conftest.py:1-2`
- **Fallback sans Docker** : `DEMO.md:167-173`
- **Gitignore** : `.gitignore:1-3`

---

## Checklist express (dernière minute)

- [ ] `./scripts/init-docker-secrets.sh` exécuté
- [ ] `docker compose up --build -d` → `docker compose ps` tout `healthy`
- [ ] `curl -s http://localhost:5000/health` → `{"status":"ok","database":"up"}`
- [ ] `LLM_PROVIDER=fake` dans `.env` (déjà)
- [ ] Terminal PowerShell ouvert avec `test_endpoints.ps1` prêt
- [ ] Slides Vault / Trivy / CI prêtes si conteneurs KO