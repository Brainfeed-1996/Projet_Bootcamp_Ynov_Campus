# DEMO_SCRIPT — Guide d'utilisation de `demo-commands.sh`

## Contexte

Le fichier `demo-commands.sh` contient l'ensemble des commandes **curl** nécessaires à la démonstration live du **Demo Day — Music Hall**. Il est conçu pour être exécuté directement dans un terminal, sans retenir les URLs ni les payloads à la main.

> **Note** : ce script n'est **pas versionné** dans le dépôt (ajoutez-le à `.gitignore`). Il sert uniquement de support de démonstration.

---

## Prérequis

| Élément | Vérification |
|---------|-------------|
| Stack Docker démarrée | `docker compose up -d --build` |
| API joignable | `curl http://localhost:5000/health` → `{"status":"ok","database":"up"}` |
| `jq` installé | `jq --version` (facultatif mais recommandé pour un JSON lisible) |
| `LLM_PROVIDER=fake` | Confirmé dans `compose.yaml` ou `.env` (fallback garanti) |

---

## Utilisation

### 1. Rendre le script exécutable (Linux / Git Bash)

```bash
chmod +x demo-commands.sh
```

### 2. S'assurer que la stack est prête

```bash
# Lancer la stack (reconstruire si nécessaire)
docker compose up -d --build

# Vérifier la santé
curl http://localhost:5000/health
```

> Si `/health` renvoie `database: down`, exécutez `docker compose restart db` puis répétez.

### 3. Exécuter le script complet

```bash
./demo-commands.sh
```

Chaque commande est précédée d'un commentaire explicatif et formatte la réponse JSON via `jq` pour une lisibilité optimale sur projet.

### 4. Exécuter une commande individuelle

Pour contrôler le timing ou répéter une étape précise, exécutez simplement la commande curl souhaitée :

```bash
# Health check seulement
curl -sS http://localhost:5000/health | jq .

# Créer un log seulement
curl -sS -X POST http://localhost:5000/logs \
  -H "Content-Type: application/json" \
  -d '{"message":"DB connection timeout","level":"ERROR","source":"api-gateway"}' | jq .
```

---

## Séquence recommandée pendant la démo

| Ordre | Endpoint | Orateur | Durée estimée |
|-------|----------|---------|---------------|
| 1 | `GET /health` | B | 5 s |
| 2 | `POST /users` | A | 5 s |
| 3 | `POST /logs` | A | 5 s |
| 4 | `POST /logs/1/analyze` | B | 5 s |
| 5 | `GET /logs?level=ERROR&limit=5` | A | 5 s |
| 6 | `GET /analyses` | B | 5 s |

---

## Plan de secours

### LLM indisponible

Si l'analyse échoue ou est lente, forcer le provider factice :

```bash
docker compose -f compose.yaml -f compose.fake.yml up -d --build web
```

Puis relancer `./demo-commands.sh`.

### `jq` absent

Sur Git Bash (Windows), `jq` peut ne pas être installé. La version sans formatage fonctionne également :

```bash
# Sans pipe vers jq (JSON brut dans le terminal)
curl -sS http://localhost:5000/health
```

Pour installer `jq` sous Git Bash :

```bash
curl -sL https://github.com/jqlang/jq/releases/download/jq-1.7.1/jq-linux-amd64 -o /usr/local/bin/jq
chmod +x /usr/local/bin/jq
```

---

## Vérification post-démo

Une fois la démonstration terminée, validez que tout est en ordre :

```bash
# 16 tests unitaires passent en moins de 3 secondes
pytest -v

# Aucune CVE HIGH/CRITICAL sur l'image
trivy image music-hall:latest
```

---

## Checklist de lancement (à cocher avant le Demo Day)

- [ ] `demo-commands.sh` rendu exécutable (`chmod +x`)
- [ ] Stack `docker compose up -d --build` sans erreur
- [ ] `curl /health` renvoie `{"status":"ok","database":"up"}`
- [ ] `LLM_PROVIDER=fake` confirmé dans l'environnement
- [ ] `jq` installé et fonctionnel
- [ ] Script testé une dernière fois : `./demo-commands.sh`
- [ ] Chronomètre visible et écrans prêts
