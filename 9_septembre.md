# Jour 3 — Mercredi 9 septembre : Conteneurisation Docker & scripting Python

## Résumé exécutif

Le troisième journée du projet *« Des logs bruts à une alerte exploitable »* marque le tournant vers l’industrialisation : on aborde Docker pour rendre les composants reproductibles et portables, puis on introduit Python comme langage pivot pour parser et valider les logs. Le fil rouge atteint **Jalon 3** : un endpoint HTTP `POST /logs` est exposé derrière un conteneur, avec ingestion en temps réel d’évènements JSON/CSV, validation stricte et traçabilité. À 12h, chaque groupe restitue sa stratégie de Dockerfile pour discuter des bonnes pratiques d’imagerisation.

---

## Objectifs pédagogiques

| Domaine | Objectif |
|---|---|
| **Docker** | Comprendre la différence VM vs conteneur, maîtriser les commandes de base (`run`, `ps`, `logs`, `exec`), écrire un Dockerfile optimisé |
| **Python** | Maîtriser types, conditions, boucles, fonctions, modules ; parser JSON/CSV ; valider des schémas simples |
| **Intégration** | Exposer un endpoint `POST /logs` dans un conteneur ; orchestrer avec `docker-compose` |
| **Sécurité** | Appliquer le principe du moindre privilège dans les images Docker (non-root, image légère) |

---

## Détail horaire

### 09h00–09h40 — Docker & introduction Python

#### VM vs conteneurs (10 min)

| Critère | Machine virtuelle | Conteneur |
|---|---|---|
| Isolation | Système invité + noyau invitée | Namespace Linux |
| Démarrage | 1–5 min | < 1 s |
| Poids | Gigabyte | Megabyte |
| Partage des ressources | Allocation statique | Cgroups dynamiques |
| Use case | OSes multiples, forte isolation | Micro-services, CI/CD |

> ℹ️ Docker n’est pas une machine virtuelle: il partage le noyau hôte. Un conteneur Windows ne peut pas tourner sur un noyau Linux — et vice-versa.

#### Rappel Python express (30 min)

```python
# Variables & types
version: str = "1.0"
count: int = 42
is_valid: bool = True
tags: list[str] = ["firewall", "ids"]
payload: dict[str, str] = {"src": "10.0.0.1", "dst": "8.8.8.8"}

# Conditions
if count > 0 and is_valid:
    severity = "HIGH" if count > 10 else "LOW"

# Boucles
for tag in tags:
    print(f"analyse: {tag}")

while count > 0:
    count -= 1

# Fonctions
def parse_log(line: str) -> dict | None:
    """Parse une ligne de log en dictionnaire."""
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None
```

Syntaxe clé à retenir:
- Pas de `var` ou `let`, c’est l’interpréteur qui infère.
- Indentation **obligatoire** (4 espaces, pas de tabs).
- Typage optionnel (annotations `: str`, `: list[str]`), mais très utile pour le parsing.

---

### 09h40–10h30 — Premier conteneur & parser Python

#### Commandes Docker de base

```bash
# Télécharger une image
docker pull python:3.12-slim

# Lancer un conteneur interactif
docker run --name parser-dev -it python:3.12-slim bash

# Lister les conteneurs
docker ps -a

# Voir les logs en temps réel
docker logs -f parser-dev

# Exécuter une commande dans un conteneur existant
docker exec -it parser-dev python --version

# Arrêter / supprimer
docker stop parser-dev && docker rm parser-dev
```

> ⚠️ `--rm` supprime le conteneur à l’arrêt. Utilisez-le pour les conteneurs éphémères: `docker run --rm python:3.12-slim echo "hello"`.

#### Dockerfile minimal

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "parser.py"]
```

Construction & exécution:

```bash
docker build -t parser:v1 .
docker run --rm -p 8000:8000 parser:v1
```

#### Parser Python : logs JSON & CSV

##### Parser JSON

Un log JSON typique généré par un SIEM:

```json
{"timestamp":"2025-09-09T09:42:00Z","src_ip":"10.0.0.5","dst_ip":"192.168.1.1","port":443,"protocol":"tcp","bytes_out":1024,"severity":"high"}
```

```python
import json
from datetime import datetime
from pydantic import BaseModel, field_validator

class NetworkLog(BaseModel):
    timestamp: datetime
    src_ip: str
    dst_ip: str
    port: int
    protocol: str
    bytes_out: int
    severity: str

    @field_validator("port")
    @classmethod
    def port_in_range(cls, v: int) -> int:
        if not (0 < v <= 65535):
            raise ValueError("port out of range")
        return v

    @field_validator("severity")
    @classmethod
    def severity_known(cls, v: str) -> str:
        valid = {"low", "medium", "high", "critical"}
        if v.lower() not in valid:
            raise ValueError(f"severity must be one of {valid}")
        return v.lower()
```

##### Parser CSV

Un log CSV typique exporté d’un firewall:

```csv
timestamp,src_ip,dst_ip,port,protocol,bytes_out,severity
2025-09-09T09:42:00Z,10.0.0.5,192.168.1.1,443,tcp,1024,high
2025-09-09T09:43:00Z,10.0.0.6,8.8.8.8,53,udp,128,low
```

```python
import csv
from io import StringIO

CSV_SCHEMA = ["timestamp", "src_ip", "dst_ip", "port", "protocol", "bytes_out", "severity"]

def parse_csv_line(line: str) -> dict | None:
    reader = csv.DictReader(StringIO(line), fieldnames=CSV_SCHEMA)
    row = next(reader, None)
    if row is None:
        return None
    row["port"] = int(row["port"])
    row["bytes_out"] = int(row["bytes_out"])
    return row
```

---

### 10h30–11h30 — Fil rouge · Jalon 3

> **Contexte** : Le groupe possède déjà un parser (Jour 2) et une source de logs bruts. On doit maintenant le conteneuriser, l’exposer sur un endpoint HTTP et valider les données en entrée.

#### Architecture cible Jalon 3

```
                ┌────────────────────────────────────┐
                │     Conteneur Docker (Python)      │
                │  ┌──────────────┐  ┌────────────┐  │
logs.raw  ────► │  │ HTTP Server  │──│  Parser     │  │───► logs.validés (stdout)
  (JSON/CSV)    │  │  POST /logs   │  │  + Validate  │  │
                └─────────────────┘  └──────────────┘
                         │
                ┌────────┴────────┐
                │ docker-compose.yml │
                │  - parser:8000/tcp  │
                └───────────────────┘
```

#### Livrables attendus

##### 1. `Dockerfile` officiel

```dockerfile
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS runtime
COPY . .
USER 1000:1000
EXPOSE 8000
ENTRYPOINT ["python", "server.py"]
```

Points de conformité:
- ✅ `slim` ou `alpine` pour réduire la surface d’attaque (CVE scanner)
- ✅ Multi-stage optional: build `dev`, `runtime` séparés
- ✅ `USER non-root` (principe du moindre privilège)
- ✅ `EXPOSE` documente le port

##### 2. `compose.yaml`

```yaml
services:
  parser:
    build: .
    image: parser:jalon3
    container_name: parser-j3
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs:ro
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
```

##### 3. Parser Python (`parser.py`)

```python
import json
import csv
from io import StringIO
from typing import Union
from pydantic import ValidationError

LOG_FORMATS = {"json", "csv"}

def detect_format(line: str) -> str:
    stripped = line.strip()
    if stripped.startswith("{"):
        return "json"
    if stripped.startswith(("timestamp,")):
        return "csv"
    raise ValueError(f"format inconnu pour la ligne: {stripped[:80]}")

def validate_json(line: str) -> dict | None:
    try:
        data = json.loads(line)
        return NetworkLog(**data).model_dump()
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"[PARSE_ERROR] json: {e}")
        return None

def validate_csv(line: str) -> dict | None:
    try:
        data = parse_csv_line(line)
        return NetworkLog(**data).model_dump()
    except (ValueError, ValidationError) as e:
        print(f"[PARSE_ERROR] csv: {e}")
        return None

def ingest(line: str) -> dict | None:
    fmt = detect_format(line)
    return validate_json(line) if fmt == "json" else validate_csv(line)
```

##### 4. Endpoint `POST /logs` (`server.py`)

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="Log Ingestion API", version="3.0.0")

@app.post("/logs")
async def ingest_logs(request: Request):
    raw = await request.body()
    text = raw.decode("utf-8")
    results = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parsed = ingest(line)
        results.append({"input": line[:80], "valid": parsed is not None, "output": parsed})
    return JSONResponse(content={"processed": len(results), "results": results})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

##### 5. `requirements.txt`

```
fastapi>=0.112.0
uvicorn>=0.30.0
pydantic>=2.8.0
```

#### Definition of Done (DoD) — Jalon 3

| Critère | Check | Commentaire |
|---|---|---|
| Dockerfile présent & build réussi | ☐ | `docker build -t parser:j3 .` doit passer sans erreur |
| `compose.yaml` fonctionne | ☐ | `docker compose up --build` démarre le service en < 10 s |
| Endpoint `POST /logs` répond | ☐ | Test avec `curl -X POST http://localhost:8000/logs -d '{"valid":"json"}'` |
| Parser JSON valide | ☐ | Un log JSON malformé est rejeté avec message d’erreur |
| Parser CSV valide | ☐ | Un header CSV invalide est détecté |
| Poids image < 150 Mo | ☐ | `docker images parser:j3` affichera < 150 Mo |
| Conteneur lancé en non-root | ☐ | `docker exec` vérifie `whoami` ≠ `root` |
| Logs stdout format JSON | ☐ | Chaque ligne de sortie est `JSON.stringify`‑able |

---

### 11h30–12h00 — Mini-restitution

Chaque groupe présente son Dockerfile en 5 min chrono:

1. **Stratégie d’image** : alpine vs slim vs full
2. **Optimisations** : cache de layer, `--no-cache-dir`, multi-stage
3. **Sécurité** : user, ports exposés, secrets committés ou non
4. **Démo live** : `POST /logs` avec un payload JSON et CSV

---

## Concepts clés

### Conteneurs vs VM

| Aspect | Docker | VM |
|---|---|---|
| Isolation noyau | Namespace + Cgroups | Hypervisor + noyau invité |
| Portabilité | Image = couche (layer) | Snapshot complète |
| Versionnement | Tag + digest | Version de l’image VM |
| Resource overhead | ~50 Mo | ~1 Go |

### JSON vs CSV

| Caractéristique | JSON | CSV |
|---|---|---|
| Structure | Hiérarchique (nested dict) | Tabulaire (ligne = événement) |
| Schéma | Flexible mais non validé | Headers fixes, colonnes typées |
| Parsing | `json.loads()` | `csv.DictReader()` |
| Performance | Overhead d’objet Python | Parsing ligne par ligne plus rapide |
| Sécurité | Injection JSON rare | Injection CSV (formules Excel) |

### Parsing — bonnes pratiques

1. **Fail fast** : rejeter un log invalide plutôt que de l’insérer avec des valeurs nulles
2. **Schema validation** : utiliser `pydantic` pour valider types, ranges, enums
3. **Sanitisation** : nettoyer les chaînes (éliminer `<script>`, `=cmd`, etc.)
4. **Logging structuré** : chaque rejection = un `dict` JSON sur `stderr`

```python
import logging, json, sys

logging.basicConfig(stream=sys.stderr, level=logging.INFO,
                    format='%(message)s')

def log_rejection(line: str, error: str):
    logging.info(json.dumps({"event": "rejection", "line": line[:120],
                             "error": error}))
```

---

## Erreurs fréquentes

| Catégorie | Erreur | Solution |
|---|---|---|
| Docker | `COPY . .` copie le `.git` et `node_modules` | Utiliser `.dockerignore` |
| Docker | Image > 200 Mo | Passer à `python:3.12-slim`, `pip --no-cache-dir` |
| Docker | Conteneur plante sur le port 8000 | Vérifier `EXPOSE` et binding `-p` |
| Python | `KeyError` sur clé manquante | `dict.get("key", default)` ou `pydantic` |
| Python | `ValueError` sur conversion `int("abc")` | `try/except ValueError` explicite |
| Parsing | Log CSV avec `;` comme séparateur | `csv.reader(f, delimiter=";")` |
| Sécurité | Credentials en dur dans l’image | Utiliser `--build-arg` ou secrets mounts |
| HTTP | Endpoint ne répond pas | `curl -v -X POST ...` pour debugger |

Exemple `.dockerignore`:

```
.git
__pycache__
*.pyc
.env
*.md
docker-compose*.yml
```

---

## Connexions jours suivants

| Jour | Thème | Lien avec J3 |
|---|---|---|
| **J4** (Jeudi 10/09) | Normalisation & stockage (Elasticsearch, Logstash) | Les logs validés par `POST /logs` seront indexés dans ES |
| **J5** (Vendredi 11/09) | Détection & corrélation | Règles Sigma/AppShield injectées via l’endpoint |

---

## Pour aller plus loin — Commandes utiles

### Docker

```bash
# Analyser la taille d’une image
docker history parser:j3

# Scanner les layers avec dive (outil tiers)
dive parser:j3

# Exécuter en mode debug avec limites
docker run --rm -it --memory=128m --cpus=0.5 parser:j3 python -i

# Nettoyer les images orphelines
docker image prune -af
```

### Python

```bash
# Formater le code
ruff check . && ruff format .

# Lancer les tests unitaires
pytest tests/ -v

# Vérifier les dépendances vulnérables
pip-audit -r requirements.txt

# Profilage du parsing
python -m cProfile -s cumtime parser.py
```

### HTTP / API

```bash
# Test rapide avec curl
curl -X POST http://localhost:8000/logs \
  -H "Content-Type: application/json" \
  -d '{"timestamp":"2025-09-09T12:00:00Z","src_ip":"10.0.0.1","dst_ip":"8.8.8.8","port":443,"protocol":"tcp","bytes_out":1024,"severity":"high"}'

# Test avec fichier
curl -X POST http://localhost:8000/logs --data-binary @sample_log.json

# Healthcheck
curl -v http://localhost:8000/health
```

---

## Annexes

### Schéma de données attendu (JSON)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["timestamp", "src_ip", "dst_ip", "port", "protocol", "bytes_out", "severity"],
  "properties": {
    "timestamp": {"type": "string", "format": "date-time"},
    "src_ip": {"type": "string", "format": "ipv4"},
    "dst_ip": {"type": "string", "format": "ipv4"},
    "port": {"type": "integer", "minimum": 1, "maximum": 65535},
    "protocol": {"type": "string", "enum": ["tcp", "udp", "icmp"]},
    "bytes_out": {"type": "integer", "minimum": 0},
    "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]}
  }
}
```

### Glossaire express

| Terme | Définition |
|---|---|
| **Layer** | Couche en lecture seule dans une image Docker; un `Dockerfile` = stack de layers |
| **Namespace** | Mécanisme Linux d’isolation des processus (PID, NET, MNT) |
| **Cgroup** | Contrôle les ressources (CPU, memory) d’un groupe de processus |
| **Model pydantic** | Classe Python qui valide automatiquement les types et contraintes |
| **Uvicorn** | Serveur ASGI pour exécuter FastAPI; asynchrone et rapide |

---

*Document compilé le 9 septembre 2025 — 12h00 — fin de journée 3.*