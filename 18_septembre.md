# Jour 10 — Vendredi 18 septembre : Restitution, Demo Day & Closing

> **Thème** : De la démo technique au bilan pédagogique — transformer dix jours de travail en livrable exploitable et en apprentissage durable.

---

## 1. Résumé exécutif

Cette dernière journée clôture le projet **« Des logs bruts à une alerte exploitable »**. Chaque équipe présente une démonstration de six minutes suivie de quatre minutes de questions/réponses, avec une répartition stricte du temps de parole à 50/50 entre profils débutant et avancé. La matinée se termine par une session de feedback croisé, un bilan collectif et des recommandations concrètes pour démarrer l'année académique sur de bonnes bases techniques et méthodologiques.

**Livrable attendu** : un dépôt Git propre, une API FastAPI conteneurisée et documentée, une base PostgreSQL persistante, un pipeline d'ingestion validé, une analyse IA remplaçable, un audit de sécurité documenté, des tests automatisés et une démo maîtrisée.

---

## 2. Objectifs pédagogiques

| Objectif | Indicateur de réussite |
|----------|------------------------|
| **Savoir présenter** un système complet en 6 min chrono | Démonstration fluide, sans temps mort, scénario réaliste |
| **Répondre aux questions** techniques sous pression | Réponses précises, vocabulaire juste, pas de « je ne sais pas » évitables |
| **Évaluer** le travail des pairs avec grille critique | Feedback constructif, points forts + axes d'amélioration identifiés |
| **Synthétiser** ses acquis pour l'année à venir | Plan d'action personnel écrit (3 actions concrètes) |
| **Valider** la checklist de sortie complète | Tous les 8 points cochés, preuves à l'appui |

---

## 3. Détaillage horaire détaillé

### 09h00 – 09h15 : Accueil & vérification matérielle (15 min)

| Action | Responsable | Durée | Critère de validation |
|--------|-------------|-------|----------------------|
| Test projecteur / partage d'écran | Équipe hôte | 3 min | Image nette, résolution adaptée |
| Vérification réseau (Wi-Fi / Ethernet) | Équipe hôte | 2 min | Ping < 20 ms, bande passante > 50 Mbps |
| Lancement conteneurs `docker compose up -d` | Chaque équipe | 5 min | API répond sur `http://localhost:8000/docs` |
| Chronomètre visible (grand écran) | Animateur | 2 min | 6 min + 4 min affichés distinctement |
| Ordre de passage affiché | Animateur | 3 min | Liste équipes + créneaux horaires |

> **Astuce** : préparez un script `demo_check.sh` qui lance `docker compose up -d`, attend le healthcheck et ouvre Swagger automatiquement.

```bash
#!/usr/bin/env bash
# demo_check.sh — à placer à la racine du repo
set -euo pipefail
docker compose up -d --wait
sleep 2
curl -sf http://localhost:8000/healthz >/dev/null && echo "✅ API prête" || { echo "❌ API KO"; exit 1; }
xdg-open http://localhost:8000/docs 2>/dev/null || open http://localhost:8000/docs 2>/dev/null || true
```

### 09h15 – 11h00 : Soutenances (105 min = 10 équipes × 10 min + 5 min tampon)

**Format imposé par équipe (10 min exactes) :**

| Phase | Durée | Contenu attendu | Répartition parole |
|-------|-------|-----------------|-------------------|
| **Démonstration** | 6 min | 1. Contexte (30s) 2. Architecture (1 min) 3. Ingestion démo (1 min 30) 4. Analyse IA (1 min 30) 5. Alerte générée (1 min) 6. Sécurité & tests (1 min) | 50/50 débutant / avancé |
| **Q&A** | 4 min | Questions jury + salle (technique, choix d'architecture, limites, suite) | 50/50 débutant / avancé |

**Chronométrage strict** : un bip sonore à 5 min (1 min restante démo), à 9 min (1 min restante Q&A), à 10 min (stop net).

**Grille d'évaluation jury (remplie en direct) :**

| Critère | Poids | Échelle 1-5 |
|---------|-------|-------------|
| Clarté du scénario & narration | 20% | |
| Maîtrise technique (code, infra, sécurité) | 25% | |
| Qualité de la démo (fluidité, données réalistes) | 20% | |
| Réponses Q&A (précision, honnêteté) | 20% | |
| Répartition parole 50/50 respectée | 15% | |

### 11h00 – 11h30 : Feedback & synthèse (30 min)

| Temps | Activité | Modalités |
|-------|----------|-----------|
| 11h00-11h10 | **Feedback croisé** | Chaque équipe note 2 points forts + 1 axe d'amélioration pour l'équipe qui a présenté juste avant (tour de table) |
| 11h10-11h20 | **Synthèse jury** | 3 réussites techniques communes, 3 points de vigilance transverses, 1 « coup de cœur » |
| 11h20-11h30 | **Évaluation pédagogique** | Questionnaire rapide (Google Forms / Mentimeter) : 5 questions Likert + 1 champ libre |

### 11h30 – 12h00 : Bilan & clôture (30 min)

| Temps | Contenu |
|-------|---------|
| 11h30-11h40 | **Tour de table express** : « Mon plus grand apprentissage » + « Ma première action en rentrée » (1 min/personne) |
| 11h40-11h50 | **Conseils pour l'année** : gestion de dette technique, veille sécurité, contribution open source, certification (CKAD, OSCP, etc.) |
| 11h50-12h00 | **Remise attestations** + photo de groupe + échanges informels |

---

## 4. Concepts clés

### Démo (6 minutes)

> Une démo technique n'est **pas** une présentation PowerPoint. C'est l'exécution en conditions réelles d'un scénario métier : ingestion → analyse → alerte. Le public doit voir les logs arriver, le modèle décider, l'alerte apparaître dans l'UI ou le webhook.

**Structure narrative recommandée** :
```
« Contexte : on surveille un serveur SSH exposé. 
  Architecture : Filebeat → API FastAPI → PostgreSQL → Worker IA → Alertmanager.
  Démonstration : j'injecte 50 lignes de auth.log dont 3 bruteforce. 
  Résultat : 3 alertes « SSH_BRUTEFORCE » avec score > 0.85, enrichies en MITRE ATT&CK T1110. »
```

### Q&A (4 minutes)

| Type de question | Exemple | Bonne réponse |
|------------------|---------|---------------|
| Architecture | « Pourquoi FastAPI et pas Flask ? » | « Async natif, validation Pydantic, OpenAPI auto, perf > Flask sync » |
| Sécurité | « Comment gérez-vous les secrets ? » | « .env non commité, Docker secrets en prod, Vault en roadmap » |
| Limites | « Ça ne scale pas ? » | « Worker stateless, queue Redis, horizontal pod autoscaler K8s prévu » |
| Choix IA | « Pourquoi Ollama et pas OpenAI ? » | « RGPD, coût nul, modèle interchangeable via même interface » |

**Règle 50/50** : chronométrez chaque intervenant. Si le profil avancé a parlé 4 min sur 6, le débutant *doit* prendre les 2 min restantes + 2 min en Q&A.

### Feedback (évaluation croisée)

Utilisez le modèle **SBI** (Situation – Behavior – Impact) :
> « *Situation* : pendant la démo d'ingestion. *Behavior* : vous avez montré le code de validation Pydantic. *Impact* : on a compris comment les logs invalides sont rejetés sans casser le pipeline. »

### Évaluation (grille jury)

La grille est **partagée en amont** (J-1). Pas de surprise. Chaque critère a des descripteurs comportementaux pour 1, 3, 5.

### Bilan (rétrospective personnelle)

Chaque participant écrit **3 actions concrètes** pour la rentrée :
1. Technique (ex. : « Contribuer à un projet open source Rust par mois »)
2. Méthodologique (ex. : « Écrire les tests *avant* le code sur mon prochain side-project »)
3. Relationnelle (ex. : « Proposer une revue de code hebdomadaire à mon binôme »)

---

## 5. Checklist de sortie complète — Explications détaillées

### 1. Dépôt Git propre avec historique lisible et Pull Requests relues

| Exigence | Pourquoi | Comment vérifier |
|----------|----------|------------------|
| **Branche `main` protégée** | Pas de push direct, historique linéaire | `git log --oneline --graph` : pas de merge commits parasites |
| **Commits atomiques & messages Conventional Commits** | Bisect, revert, changelog auto | `feat: add log ingestion endpoint`<br>`fix: handle null timestamp in parser` |
| **PR relues (au moins 1 approbation)** | Revue de code = partage de connaissance | GitHub : « Approved » + commentaires résolus |
| **Pas de secrets dans l'historique** | Fuite credentials = incident | `git log --all --full-history --oneline -- "**/.env"` → vide |
| **Tags de version** | Reproductibilité | `git tag -l` → `v1.0.0-demo` présent |

**Commandes de vérification :**
```bash
# Historique propre ?
git log --oneline --graph -20

# Secrets ?
gitleaks detect --source . --verbose

# Conventional commits ?
git log --grep="^[a-z]+(" --oneline | head -10
```

---

### 2. API FastAPI documentée dans Swagger et démarrable via Docker Compose

| Élément | Attendu | Test de validation |
|---------|---------|-------------------|
| **OpenAPI 3.0 complet** | `/docs` et `/redoc` accessibles | `curl -s http://localhost:8000/openapi.json \| jq .info.title` |
| **Modèles Pydantic documentés** | Schémas request/response + exemples | Swagger UI : « Try it out » pré-rempli |
| **Healthcheck** | `GET /healthz` → `{"status":"ok"}` | `docker compose ps` → `healthy` |
| **Docker Compose one-shot** | `docker compose up -d --wait` suffit | Pas de `docker exec` manuel nécessaire |
| **Variables d'env via `.env.example`** | Pas de durcissement en dur | `cat .env.example` liste toutes les vars requises |

**`docker-compose.yml` minimal :**
```yaml
version: "3.9"
services:
  api:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
      interval: 10s
      timeout: 3s
      retries: 5
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 5s
      timeout: 3s
      retries: 5
volumes: { pgdata: {} }
```

---

### 3. PostgreSQL persistant avec schéma reproductible

| Point | Détail | Validation |
|-------|--------|------------|
| **Migrations versionnées** | Alembic ou SQL fichiers numérotés | `alembic history` ou `ls migrations/*.sql` |
| **Schéma idempotent** | `CREATE TABLE IF NOT EXISTS` | `docker compose down -v && docker compose up -d` → tables créées |
| **Données de démo incluses** | `seed.sql` ou script Python `seed.py` | `docker compose exec db psql -U user -d db -c "SELECT count(*) FROM logs;"` > 0 |
| **Index sur colonnes filtrées** | `created_at`, `source_ip`, `level` | `\d+ logs` montre index btree |
| **Utilisateur applicatif non-superuser** | Rôle `app_user` avec grants limités | `\du` → pas de `superuser` |

**Exemple migration Alembic (`versions/001_init.py`) :**
```python
def upgrade():
    op.create_table(
        "logs",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("source_ip", sa.String(45), nullable=False, index=True),
        sa.Column("level", sa.String(10), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("raw_json", sa.JSON, nullable=True),
    )
    op.create_index("ix_logs_timestamp_desc", "logs", ["timestamp"], postgresql_using="btree", postgresql_ops={"timestamp": "DESC"})

def downgrade():
    op.drop_table("logs")
```

---

### 4. Ingestion de logs JSON ou CSV avec validation et erreurs explicites

| Format | Exemple valide | Erreur type gérée |
|--------|----------------|-------------------|
| **JSON Lines** | `{"timestamp":"2024-09-18T10:00:00Z","source_ip":"1.2.3.4","level":"ERROR","message":"Failed password"}` | Champ manquant → `422 Unprocessable Entity` + détail Pydantic |
| **CSV** | `timestamp,source_ip,level,message\n2024-09-18T10:00:00Z,1.2.3.4,ERROR,Failed password` | Délimiteur inattendu → `400 Bad Request` + « Expected comma delimiter » |

**Endpoint d'ingestion (`POST /api/v1/logs/ingest`) :**
```python
@router.post("/ingest", status_code=202)
async def ingest_logs(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    parser = LogParserFactory.get_parser(file.filename)  # JSONLinesParser | CSVParser
    valid, errors = parser.parse_and_validate(file.file)
    if errors:
        return JSONResponse(
            status_code=422,
            content={"inserted": len(valid), "errors": errors[:50]},  # max 50 erreurs
        )
    inserted = await LogRepository.bulk_insert(db, valid)
    return {"inserted": inserted, "errors": []}
```

**Test rapide :**
```bash
curl -F "file=@sample_logs.jsonl" http://localhost:8000/api/v1/logs/ingest | jq
# {"inserted": 47, "errors": [{"line": 12, "error": "timestamp missing"}]}
```

---

### 5. Analyse structurée via OpenAI ou Ollama, remplaçable et testable hors ligne

**Architecture — Pattern Strategy :**
```
LogAnalyzer (protocol)
├── OpenAIAnalyzer  → appel API OpenAI (clé dans .env)
├── OllamaAnalyzer  → appel local http://ollama:11434
└── MockAnalyzer    → réponses déterministes pour tests CI
```

**Interface commune (`analyzer.py`) :**
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class AnalysisResult:
    alert_type: str
    confidence: float
    mitre_technique: str
    summary: str

class LogAnalyzer(ABC):
    @abstractmethod
    async def analyze(self, logs: list[LogEntry]) -> list[AnalysisResult]: ...
```

**Configuration via variable d'env :**
```bash
# .env
ANALYZER_BACKEND=ollama   # ou openai, mock
OLLAMA_MODEL=llama3.1:8b
OPENAI_MODEL=gpt-4o-mini
```

**Test unitaire sans réseau (`test_analyzer.py`) :**
```python
@pytest.fixture
def mock_analyzer():
    return MockAnalyzer(responses=[
        AnalysisResult("SSH_BRUTEFORCE", 0.92, "T1110", "3 échecs SSH depuis 1.2.3.4"),
        AnalysisResult("NORMAL", 0.1, "", "Connexion légitime"),
    ])

async def test_analyze_returns_expected_alerts(mock_analyzer):
    logs = [LogEntry(...), LogEntry(...)]
    results = await mock_analyzer.analyze(logs)
    assert results[0].alert_type == "SSH_BRUTEFORCE"
    assert results[0].confidence > 0.9
```

**Démo** : basculer `ANALYZER_BACKEND=mock` → démo instantanée, pas de latence, pas de coût.

---

### 6. Audit de sécurité et remédiations prioritaires documentés

**Fichier `SECURITY_AUDIT.md` à la racine du repo :**

```markdown
# Audit de sécurité — Projet Logs-to-Alert

## Méthodologie
- OWASP Top 10 2021 + ASVS Level 1
- Outils : bandit, safety, trivy, semgrep, OWASP ZAP (scan passif)

## Résultats — Top 5 critiques

| ID | Vulnérabilité | Criticité | Fichier | Remédiation | Statut |
|----|---------------|-----------|---------|-------------|--------|
| S-01 | Injection SQL potentielle via `raw_json` | 🔴 Critique | `repositories/log_repo.py:42` | Requêtes paramétrées uniquement, interdire `text()` brut | ✅ Corrigé |
| S-02 | Secrets en dur dans `docker-compose.yml` | 🔴 Critique | `docker-compose.yml:12` | Variables d'env + Docker secrets / Vault | ✅ Corrigé |
| S-03 | Pas de rate limiting sur `/ingest` | 🟠 Haute | `main.py` | Ajouter `slowapi` + limite 100 req/min/IP | 🟡 En cours |
| S-04 | CORS trop permissif (`allow_origins=["*"]`) | 🟠 Haute | `main.py:28` | Restreindre aux domaines front connus | ✅ Corrigé |
| S-05 | Image de base non scannée | 🟡 Moyenne | `Dockerfile:1` | `trivy image --severity HIGH,CRITICAL myapi:latest` | 🟡 Planifié |

## Preuves de correction (extrait)
```bash
# S-01 : bandit ne trouve plus d'injection
bandit -r . -ll -f json | jq '.results[] | select(.test_id=="B608")'  # vide

# S-02 : pas de secret dans l'image
trivy fs --security-checks secret .
```
```

---

### 7. Tests automatisés, README de démarrage et jeu de données de démonstration

| Composant | Couverture minimale | Commande de vérification |
|-----------|---------------------|--------------------------|
| **Tests unitaires** | ≥ 80% lignes (core: parser, analyzer, repo) | `pytest --cov=app --cov-report=term-missing --cov-fail-under=80` |
| **Tests d'intégration** | Ingestion → DB → Analyse → Alerte | `pytest tests/integration -v` |
| **Tests de contrat** | Schéma OpenAPI respecté | `schemathesis run --stateful=links http://localhost:8000/openapi.json` |
| **README.md** | Sections : Architecture, Démarrage rapide, Variables d'env, Démo, Tests, Dépannage | `head -100 README.md` |
| **Jeu de données** | `sample_logs.jsonl` (200 lignes), `sample_logs.csv` (200 lignes), mix normal/attaque | `wc -l sample_logs.*` |

**README — section « Démarrage rapide » :**
```markdown
## 🚀 Démarrage rapide (30 secondes)

```bash
git clone https://github.com/yourorg/logs-to-alert.git
cd logs-to-alert
cp .env.example .env          # éditez si besoin
docker compose up -d --wait   #ビルド + healthcheck
open http://localhost:8000/docs
```

## 🎬 Lancer la démo

```bash
./scripts/run_demo.sh         # injecte sample_logs.jsonl, affiche alertes
```

## 🧪 Tests

```bash
pytest                    # unit + integration
pytest --cov=app         # avec couverture
```
```

**`scripts/run_demo.sh` :**
```bash
#!/usr/bin/env bash
set -euo pipefail
echo "📥 Injection des logs de démo..."
curl -s -F "file=@sample_logs.jsonl" http://localhost:8000/api/v1/logs/ingest | jq
echo "🔍 Récupération des alertes générées..."
curl -s http://localhost:8000/api/v1/alerts | jq '.[] | {type: .alert_type, confidence: .confidence, mitre: .mitre_technique}'
```

---

### 8. Démo de six minutes suivie de quatre minutes de questions, parole répartie à 50/50

**Chronométrage individuel (exemple pour binôme) :**

| Minute | Intervenant | Contenu |
|--------|-------------|---------|
| 0:00 – 0:30 | Débutant | Contexte métier + architecture (1 slide ou schéma tableau) |
| 0:30 – 1:30 | Avancé | Pipeline technique : ingestion → validation → file d'attente |
| 1:30 – 3:00 | Débutant | Démonstration live : `./scripts/run_demo.sh` + commentaires |
| 3:00 – 4:30 | Avancé | Analyse IA : prompt, modèle, parsing réponse, mapping MITRE |
| 4:30 – 5:30 | Débutant | Sécurité : audit, corrections, rate limiting, secrets |
| 5:30 – 6:00 | Avancé | Tests, CI/CD, observabilité (logs structurés, métriques Prometheus) |
| 6:00 – 10:00 | **Q&A** | Alternance : 1 question → débutant répond, 1 question → avancé répond |

**Fiche de préparation démo (à imprimer) :**
```
☐ Conteneurs démarrés (docker compose ps → healthy)
☐ Jeu de données sample_logs.jsonl présent
☐ Script run_demo.sh testé hier (durée < 90s)
☐ Swagger ouvert onglet /ingest + /alerts
☐ Chronomètre visible (tel. ou grand écran)
☐ Fiche réponses Q&A types préparée
☐ Répartition parole validée à l'oral (répétition 1x)
```

---

## 6. Erreurs fréquentes lors de la démo (et comment les éviter)

| Erreur | Conséquence | Parade |
|--------|-------------|--------|
| **Pas de plan B** (démo live only) | Panne réseau / API down = démo ratée | Préparer **vidéo 2 min** (asciinema / OBS) + captures d'écran annotées |
| **Un profil prend tout le temps** | Note 50/50 non respectée → pénalité jury | Chronomètre individuel + répétition chronométrée J-1 |
| **Matériel non testé à l'avance** | Projecteur HS, son absent, résolution mauvaise | Checklist 09h00-09h15 **obligatoire**, responsable désigné |
| **Données de démo non réalistes** | Jury ne comprend pas la valeur métier | Utiliser *vrais* logs anonymisés (auth.log, nginx, CloudTrail) |
| **Réponses Q&A improvisées** | « Je ne sais pas » sur choix d'architecture | Fiche « Pourquoi ce choix ? » préparée par item (DB, IA, FW, etc.) |
| **Pas de nettoyage entre passages** | Données résiduelles polluent la démo suivante | `docker compose down -v && docker compose up -d --wait` scripté |

---

## 7. Connexions avec tout le projet

| Jour | Apport au Demo Day | Preuve attendue en démo |
|------|-------------------|-------------------------|
| J1 – Fondations DevSecOps | Culture « security by design », git, CI | Historique Git propre, PR relues |
| J2 – Ingestion & validation | Parser robuste, erreurs explicites | `POST /ingest` gère JSON/CSV + 422 détaillé |
| J3 – Stockage & modélisation | PostgreSQL + migrations + index | Schéma reproductible, requêtes < 50 ms |
| J4 – API FastAPI | REST documenté, auth JWT, rate limit | Swagger complet, `/healthz`, 401/429 testés |
| J5 – Analyse IA | Prompt engineering, modèle interchangeable | Basculement OpenAI ↔ Ollama ↔ Mock via `.env` |
| J6 – Alerte & enrichissement | Mapping MITRE, webhook Alertmanager | Alerte JSON avec `mitre_technique`, `confidence` |
| J7 – Sécurité & audit | Bandit, Trivy, OWASP ZAP, remédiations | `SECURITY_AUDIT.md` + corrections prouvées |
| J8 – Tests & qualité | PyTest, coverage, Schemathesis, pre-commit | `pytest --cov-fail-under=80` passe en CI |
| J9 – Observabilité & runbooks | Logs structurés, métriques, runbook incident | Dashboard Grafana (optionnel) + `RUNBOOK.md` |
| **J10 – Demo Day** | **Synthèse + communication + bilan** | **Démo 6 min + Q&A 4 min + feedback + plan personnel** |

---

## 8. Pour aller plus loin — Conseils pour la suite

### 🎯 Court terme (premier mois de rentrée)

1. **Publiez le repo en public** (si licence le permet) → portfolio GitHub, README soigné, badges CI.
2. **Soumettez un talk** 15 min à un meetup local (DevSecOps, Python, Sécurité) — la démo est prête.
3. **Automatisez le déploiement** : GitHub Actions → Docker Hub → Kubernetes (kind/k3d local → cloud).
4. **Ajoutez de l'observabilité réelle** : Prometheus + Grafana + Loki + Tempo (stack LGTM).

### 📚 Moyen terme (premier semestre)

| Compétence | Ressource | Certification visée |
|------------|-----------|---------------------|
| **Kubernetes sécurité** | CKS (Certified Kubernetes Security Specialist) | CKS |
| **Cloud natif** | CNCF Landscape, Terraform, Helm | CKA / CKAD |
| **Threat modeling** | STRIDE, PASTA, OWASP Threat Dragon | — |
| **Développement sécurisé** | Secure Code Warrior, OWASP SAMM | — |
| **Rust / Go pour outils sécurité** | `ripgrep`, `fd`, `trivy` sont en Rust/Go | — |

### 🤝 Long terme (carrière)

- **Contribuez** : trouvez un projet CNCF Sandbox/Incubating (Falco, Kyverno, Trivy…) et ouvrez une PR par mois.
- **Mentorez** : encadrez des juniors sur des CTF, des projets open source, des revues de code.
- **Veille active** : 30 min/semaine — The Daily Swig, Dark Reading, blog GitHub Security, RSS CVE critiques.
- **Spécialisez-vous** : Supply Chain Security (SLSA, Sigstore), eBPF runtime security, Zero Trust Architecture.

---

> **« Ce qu'on ne peut pas mesurer, on ne peut pas améliorer. Ce qu'on ne peut pas démontrer, on ne peut pas vendre. Ce qu'on ne partage pas, on l'oublie. »**  
> — Prenez ce projet comme **premier artefact** de votre portfolio DevSecOps. Faites-en une référence, pas une archive.

---

*Document généré pour le projet « Des logs bruts à une alerte exploitable » — Ynov Campus — Septembre 2026*