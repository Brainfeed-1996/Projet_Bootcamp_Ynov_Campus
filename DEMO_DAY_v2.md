# Mise à jour Demo Day — Corrections v2.0

Ce document complète `DEMO_DAY.md` avec les changements apportés pour la version finale.

---

## Nouveautés Démonstrables (v2.0)

### 1. Endpoint GET /alerts (NOUVEAU - Contrat API #6)
```bash
# Créer des logs avec analyses HIGH/CRITICAL
curl -X POST http://localhost:5000/logs -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"SQL injection attempt","level":"ERROR","source":"web"}'

curl -X POST http://localhost:5000/logs/1/analyze -H "Authorization: Bearer $TOKEN"
# (avec provider custom retournant HIGH/CRITICAL)

# Lister les alertes
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/alerts
# Retourne uniquement analyses HIGH + CRITICAL
```

### 2. Authentification JWT (NOUVEAU)
```bash
# 1. Login
curl -X POST http://localhost:5000/auth/login \
  -d "username=admin&password=AdminPass123"
# {"access_token":"eyJ...","token_type":"bearer"}

# 2. Utiliser le token
export TOKEN="eyJ..."
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/logs
```

**Rôles démo** :
- `admin` / `AdminPass123` → tous droits
- `writer` / `WriterPass123` → écriture logs/analyses
- `reader` / `ReaderPass123` → lecture seule

### 3. Modèles de données complets (Conformes cours.md)
```bash
# Log avec occurred_at + metadata
curl -X POST http://localhost:5000/logs -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message":"Test complet",
    "level":"WARNING",
    "source":"demo",
    "occurred_at":"2026-09-13T10:00:00Z",
    "metadata":{"request_id":"req-123","user_id":42}
  }'

# Réponse inclut occurred_at et metadata
# {"id":1,"occurred_at":"2026-09-13T10:00:00+00:00","level":"WARNING",...,"metadata":"{\"request_id\":\"req-123\",\"user_id\":42}"}
```

### 4. Analyse IA avec provider tracking
```bash
curl -X POST http://localhost:5000/logs/1/analyze -H "Authorization: Bearer $TOKEN"
# Réponse inclut provider utilisé
# {"id":1,"log_id":1,"severity":"LOW","category":"TEST","summary":"...","recommendations":["..."],"provider":"fake"}
```

### 5. Sanitization automatique avant LLM
```bash
# Log avec données sensibles
curl -X POST http://localhost:5000/logs -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"User alice@example.com from 192.168.1.1 password=secret123","level":"INFO","source":"auth"}'

# Analyse → données sensibles remplacées avant envoi au provider
# [EMAIL_REDACTED], [IP_REDACTED], [CREDENTIAL_REDACTED]
```

### 6. Security Headers visibles
```bash
curl -I http://localhost:5000/health
# HTTP/1.1 200 OK
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
# Content-Security-Policy: default-src 'self'; ...
```

---

## Commandes Demo Day Mises à Jour

Ajouter à `demo-commands.sh` :

```bash
#!/bin/bash
# Commandes Demo Day v2.0 — pré-testées

# 1. Health check (public)
curl -s http://localhost:5000/health | jq

# 2. Login admin
TOKEN=$(curl -s -X POST http://localhost:5000/auth/login \
  -d "username=admin&password=AdminPass123" | jq -r .access_token)
echo "Token: $TOKEN"

# 3. Créer un log complet
curl -s -X POST http://localhost:5000/logs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"DB connection timeout","level":"ERROR","source":"api-gateway","occurred_at":"2026-09-13T10:00:00Z","metadata":{"trace_id":"abc-123"}}' | jq

# 4. Analyser (fake provider)
curl -s -X POST http://localhost:5000/logs/1/analyze \
  -H "Authorization: Bearer $TOKEN" | jq

# 5. Lister logs filtrés
curl -s "http://localhost:5000/logs?level=ERROR&limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq

# 6. Alertes (HIGH/CRITICAL only)
curl -s http://localhost:5000/alerts \
  -H "Authorization: Bearer $TOKEN" | jq

# 7. Sanitization demo
curl -s -X POST http://localhost:5000/logs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"User alice@example.com from 192.168.1.1 pwd=secret","level":"INFO","source":"auth"}' | jq

# 8. Security headers
curl -sI http://localhost:5000/health | grep -iE "x-content-type|x-frame|x-xss|content-security"
```

---

## Points de Démonstration Clés (6 min)

| Minute | Orateur | Action | Point Clé |
|--------|---------|--------|-----------|
| 0:00-0:30 | A | Intro + Architecture | "API complète DevSecOps" |
| 0:30-1:15 | B | Auth JWT + RBAC | Login, roles admin/writer/reader |
| 1:15-2:00 | A | Créer log complet | occurred_at, metadata, validation |
| 2:00-2:45 | B | Analyser + Sanitizer | Provider fake, PII redacted |
| 2:45-3:30 | A | Alertes GET /alerts | Filtre HIGH/CRITICAL |
| 3:30-4:15 | B | Security headers + Rate limit | Headers, middleware, taille max |
| 4:15-5:00 | A | CI/CD + Trivy bloquant | Pipeline, actions SHA |
| 5:00-5:45 | B | Secrets + Vault | Docker Secrets, init script |
| 5:45-6:00 | A+B | Closing | DoD validé, tag v1.0.0 |

---

## Plans de Secours Mis à Jour

| Scénario | Solution v2.0 |
|----------|---------------|
| Auth échoue | Vérifier users créés au bootstrap (`_bootstrap_all()` dans tests) |
| Provider IA down | `LLM_PROVIDER=fake` déjà par défaut, pas de breaking change |
| DB down | Healthcheck + restart policy `on-failure` |
| Secrets manquants | `./scripts/init-docker-secrets.sh` recrée passwords identiques |
| Port 5000 occupé | `docker compose down` + changer port dans compose.yaml |
| Tests lents | `pytest -x -q` pour arrêt rapide |

---

## Checklist Pré-Demo v2.0

- [ ] `docker compose up --build -d` : services healthy
- [ ] `curl /health` → `{"status":"ok","database":"up"}`
- [ ] Login admin → token valide
- [ ] `POST /logs` avec occurred_at/metadata → 201
- [ ] `POST /logs/1/analyze` → provider="fake", severity LOW
- [ ] `GET /alerts` → liste HIGH/CRITICAL (après injection analyses test)
- [ ] `GET /logs` avec filtres → fonctionne
- [ ] Security headers présents sur `/health`
- [ ] `pytest -q` → 72 passed
- [ ] `docker compose -f compose.yaml -f docker-compose.production.yml config --quiet` → OK
- [ ] `./scripts/init-docker-secrets.sh` → passwords identiques app+PG

---

*Document mis à jour le 2026-09-13 pour Demo Day v2.0*