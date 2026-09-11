# DEMO.md — Support Demo Day

**Durée** : 6 minutes de démonstration + Q&A  
**Orateurs** : Presenter A (Scott) + Presenter B (alterne)  
**Répartition** : 50/50 du temps de parole  
**Public** : Ynov — Défensive / DevSecOps  
**Environnement** : `fake` provider par défaut, aucune IA réelle, aucun réseau.

---

## Checklist pré-démo

- [ ] `docker compose up --build -d` et services sains.
- [ ] Terminal prêt : `curl`, `docker compose logs`, `trivy` si disponible.
- [ ] `/health` accessible : `http://localhost:5000/health`.
- [ ] `README.md` et `DEMO.md` visibles.
- [ ] `.env` / `.env.production.example` / `.gitignore` visibles pour la partie secrets.

---

## Minute 0:00–0:30 — Introduction (Presenter A, 50/50)

**Commandes** : aucune (slide / oral).

Points clés :
- Log Sentinel API : ingestion et analyse de logs sécurisée.
- Stack : FastAPI + PostgreSQL + Docker + Trivy + Vault.
- Démo en 6 minutes : secrets, validation, durcissement, scan, Vault.

---

## Minute 0:30–1:30 — Secrets et `.gitignore` (Presenter B)

**Commandes** :

```bash
cat .gitignore
cat .env.production.example
ls -la secrets || true
```

Points clés :
- `.env` et `.env.production` ignorés par Git et Docker.
- Secrets montés via Docker Secrets ou Vault en production.
- `scripts/init-docker-secrets.sh` pour le développement local.

Résultat attendu : `.env` absent de Git, `.env.production.example` avec placeholders.

---

## Minute 1:30–2:30 — Validation des entrées (Presenter A)

**Commandes** :

```bash
curl -s http://localhost:5000/health
curl -s http://localhost:5000/users/1
curl -s -X POST http://localhost:5000/users -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"SuperSecret1"}'
curl -s -X POST http://localhost:5000/users -H "Content-Type: application/json" \
  -d '{"username":"al","email":"bad","password":"short"}'
curl -s -X POST http://localhost:5000/logs -H "Content-Type: application/json" \
  -d '{"message":"Connection timeout","level":"BOGUS"}'
```

Points clés :
- Types et plages validées par FastAPI et Pydantic.
- Mots de passe hachés avec bcrypt, jamais en clair.
- Messages de rejet explicites.

Résultat attendu : 201 utilisateur, 422 validation, 422 niveau invalide.

---

## Minute 2:30–3:30 — Durcissement conteneur (Presenter B)

**Commandes** :

```bash
docker compose ps
docker inspect music-hall-web-1 | grep -i user
docker inspect music-hall-web-1 | grep -i readonly
docker inspect music-hall-web-1 | grep -i cap_drop
```

Points clés :
- Utilisateur non-root `appuser` (UID 1000).
- `read_only: true` et `tmpfs` pour `/tmp`.
- `cap_drop: ALL` en production.
- Scan Trivy en CI ; HIGH/CRITICAL bloque le pipeline.

Résultat attendu : UID 1000:1000, ReadOnly true, cap-drop ALL.

---

## Minute 3:30–4:30 — Analyse de logs sans IA réelle (Presenter A)

**Commandes** :

```bash
curl -s -X POST http://localhost:5000/logs -H "Content-Type: application/json" \
  -d '{"message":"Connection timeout from api","level":"ERROR","source":"api"}' | jq .id
curl -s -X POST http://localhost:5000/logs/1/analyze
curl -s http://localhost:5000/analyses
```

Points clés :
- Provider `fake` par défaut, déterministe et offline.
- OpenAI / Ollama pluggables via `LLM_PROVIDER`.
- Réponses validées et normalisées.

Résultat attendu : analyse LOW, recommendations list, durée < 1s.

---

## Minute 4:30–5:30 — Sécurité avancée / Vault (Presenter B)

**Commandes** :

```bash
sed -n '1,120p' docker-compose.vault.yml
sed -n '1,120p' config/vault-agent/agent.hcl
docker compose config
```

Points clés :
- Docker Secrets pour le développement.
- Vault optionnel pour production : agent lit les secrets, jamais codés.
- `.env.production.example` et scripts d'init documentés.

Résultat attendu : `docker-compose.vault.yml` valide, `config/vault-agent/agent.hcl` visible.

---

## Minute 5:30–6:00 — Conclusion et handoff (Presenter A)

**Commandes** :

```bash
curl -s http://localhost:5000/health
git status --short
```

Points clés :
- Recap : secrets, validation, durcissement, scan, Vault.
- Shift-left : trouver tôt, corriger à moindre coût.
- Shift-right : santé, logs, monitoring.
- Repository propre, tag `v1.0.0`, DoD validé.

Résultat attendu : health 200, aucun fichier sensitive modifié.

---

## Q&A (4 minutes)

| Question | Réponse |
|----------|---------|
| Pourquoi `.env` est-il ignoré ? | Secrets never in code; production uses env vars, Docker Secrets, or Vault. |
| Comment sont stockés les mots de passe ? | bcrypt, irréversible et salé. |
| Que fait Trivy ? | Scanne HIGH/CRITICAL et bloque le build si vulnérabilités. |
| Comment tester sans IA ? | `LLM_PROVIDER=fake`, SQLite in-memory, `TESTING=1`. |
| Pourquoi read_only ? | Surface d'attaque réduite, écritures limitées à tmpfs. |
| D'où viennent les secrets en prod ? | Docker Secrets montés via fichiers ou Vault Agent. |

---

## Plan de secours sans IA / sans Docker

Si le conteneur ne démarre pas :

```bash
TESTING=1 python -m pytest -v
```

Les tests utilisent un fournisseur factice et une base SQLite en mémoire. Aucune connexion réseau n'est requise.
