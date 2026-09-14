# Jour 5 — Vendredi 11 septembre

## Cyber défensive & DevSecOps : Des logs bruts à une alerte exploitable

> **Semaine 1 — Socle systèmes, infrastructure et début du projet**
> Jalon 5 : Sécurisation de l'application

---

## 1. Résumé exécutif du jour

Ce jour est le **point culminant de la semaine 1**. Après quatre jours passés à installer des environnements, manipuler Linux, conteneuriser avec Docker et découvrir la cyber offensive (OWASP, CTF), nous basculons en mode **défensif**. L'objectif est triple :

1. **Comprendre les principes fondamentaux** du Secure Coding et de l'approche DevSecOps.
2. **Pratiquer le nettoyage** d'un dépôt contenant des secrets compromis et apprendre à isoler les configurations sensibles avec `.env`, `.gitignore` et `python-dotenv`.
3. **Finaliser le Jalon 5** : valider strictement toutes les entrées de l'API et garantir qu'aucun secret ne se trouve dans l'image Docker.

À l'issue de cette journée, l'application doit être en mesure de recevoir des événements techniques, de les valider rigoureusement avant toute insertion en base ou tout appel au moteur IA, et de tourner dans un conteneur dont aucune configuration secrète ne fuit.

> **Pourquoi ce jour est crucial pour le projet global** : les jours suivants introduisent PostgreSQL (jour 6), l'intégration IA (jour 7) puis le sprint de développement (jours 8-10). Si les entrées ne sont pas validées maintenant, chaque donnée malformée polluera la base, chaque appel IA recevra du contenu inapproprié, et les analyses produites seront sans valeur. La sécurisation est le socle sur lequel tout le reste repose.

---

## 2. Objectifs pédagogiques

À la fin de cette journée, chaque binôme sera capable de :

- **Définir** ce qu'est le Secure Coding et expliquer les principes DevSecOps (shift-left, shift-right).
- **Distinguer** le hachage de mots de passe (bcrypt, argon2) du chiffrement de données (AES, TLS) et savoir quand utiliser l'un ou l'autre.
- **Isoler** les secrets à l'aide de fichiers `.env`, `.env.example` et `.gitignore`.
- **Nettoyer** un dépôt Git qui contiendrait des clés ou mots de passe compromis.
- **Charger** une configuration via `python-dotenv` dans une application Python.
- **Valider strictement** les entrées utilisateur au niveau de l'API (type, longueur, format, valeurs autorisées).
- **Durcir** un conteneur Docker : utilisateur non-root, filesystem en lecture seule, suppression des privilèges excessifs.
- **Produire** les livrables du Jalon 5 : `.env.example` documenté, `.gitignore` vérifié, configuration Docker sans secret dans l'image.

---

## 3. Détaillage horaire

### 3.1. 09h00–09h40 — Sécurisation & Clean Code (40 min)

> **Thèmes** : Secure Coding, principes DevSecOps, isolation des secrets avec `.env` et `.gitignore`, distinction hachage bcrypt/argon2 vs chiffrement.

#### 3.1.1. Secure Coding — Écrire du code qui résiste

Le **Secure Coding** consiste à écrire du code conçu pour résister aux attaques courantes. Ce n'est pas un supplément de travail : c'est une manière de programmer qui empêche dès la source les erreurs les plus fréquentes.

Les menaces les plus courantes auxquelles notre API sera confrontée :

- **Injection SQL** : un utilisateur saisit `' OR 1=1 --` dans un champ censé être un identifiant. Si cette chaîne est collée directement dans une requête SQL, l'attaquant peut lire ou modifier toute la base.
- **Cross-Site Scripting (XSS)** : un utilisateur soumet un log dont le message contient `<script>alert('pirate')</script>`. Si ce message est affiché sans échappement, le navigateur de chaque visiteur exécutera le script.
- **Dépassement de taille (DoS)** : un client envoie un corps de requête de 500 Mo. Sans limite, le serveur s'essouffle.
- **Fuite de secrets** : une erreur interne affiche dans la réponse JSON la pile d'appels complète, révélant des noms de fichiers, des chemins et parfois des clés.

> **Principe fondamental** : traitez toute entrée comme non fiable, même lorsqu'elle provient de votre propre interface ou d'un outil de démonstration.

**Exemple concret** — Requête préparée vs concaténation :

```python
# ❌ DANGEREUX — Injection SQL possible
query = f"SELECT * FROM logs WHERE id = {user_id}"

# ✅ SÛR — Le pilote échappe automatiquement la valeur
query = text("SELECT * FROM logs WHERE id = :user_id")
result = db.execute(query, {"user_id": user_id})
```

#### 3.1.2. Principes DevSecOps

Le DevSecOps intègre la sécurité dans chaque étape du cycle de développement, et non en fin de chaîne.

- **Shift-left** : détecter les problèmes le plus tôt possible. Un bug de sécurité repéré en phase de codage coûte 1× à corriger. Repéré en production, il coûte 100×.
- **Shift-right** : monitorer en production (logs, alertes, réponses automatiques) pour détecter ce que les tests n'ont pas vu.
- **Automatisation** : les analyses de vulnérabilités (SAST, scan de dépendances, scan d'image Docker) doivent être déclenchées automatiquement dans le pipeline CI, sans intervention humaine.

> **En pratique dans ce projet** : Trivy scanne l'image Docker à chaque build, Snyk analyse les dépendances Python, et la validation Pydantic rejette les entrées invalides avant qu'elles n'atteignent la base de données.

#### 3.1.3. Isoler les secrets avec `.env` et `.gitignore`

Un **secret** est toute valeur qui doit rester privée : mot de passe, jeton d'accès, clé API, certificat, URL de base contenant un mot de passe.

Les règles sont simples et absolues :

- ** Jamais dans le code source.** Pas de `SECRET_KEY = "abc123"` dans un fichier Python.
- **Jamais dans Git.** Même si vous supprimez le fichier ensuite, l'historique conserve la valeur.
- **Dans un fichier `.env`** pour le développement local, lu par `python-dotenv`.
- **Dans des variables d'environnement du système** ou des secrets Docker pour la production.
- **`.gitignore`** doit contenir `.env`, `.env.production`, `secrets/`, et tout répertoire contenant des valeurs réelles.

#### 3.1.4. Hachage vs Chiffrement — Une distinction capitale

| Concept | Définition | Réversible ? | Usage principal | Exemple |
|---------|-----------|:---:|---|---|
| **Hachage** | Transformation unidirectionnelle d'une donnée en empreinte fixe | Non (irréversible) | Stockage de mots de passe | bcrypt, argon2, scrypt |
| **Chiffrement** | Transformation bidirectionnelle d'une donnée en forme illisible | Oui (avec la clé) | Données sensibles à récupérer | AES, TLS, Fernet |

> **Règle d'or** : On **hache** les mots de passe (on ne doit jamais pouvoir les retrouver). On **chiffre** les données qu'on devra restituer (numéros de carte, adresses, clés de configuration).

**Pourquoi bcrypt ?** bcrypt est conçu pour être lent (paramétrable en coût), ce qui rend les attaques par force brute économiquement inviables. Argon2 va plus loin en consommant de la mémoire, ce qui rend les attaques avec des GPU ou des FPGA inefficaces. Les deux sont préférables à MD5 ou SHA-1, qui sont rapides et compromise.

**Exemple concret** :

```python
# ❌ Ne JAMAIS stocker un mot de passe en clair ou haché avec MD5
password = "MonMotDePasse2024"
# MD5 → rapide, rainbow tables → craqué en millisecondes

# ✅ Hacher avec bcrypt (ou scrypt via Werkzeug)
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
# Vérification ultérieure :
bcrypt.checkpw(password.encode(), hashed)  # → True
```

---

### 3.2. 09h40–10h30 — Hardening & variables d'environnement (50 min)

> **Thèmes** : Nettoyer un dépôt fictif contenant des clés compromises, utiliser `python-dotenv` pour charger la configuration.

#### 3.2.1. Nettoyer un dépôt avec des secrets compromis

Scénario réaliste : un développeur a committé par erreur un fichier `.env` contenant `SECRET_KEY=dev_secret_key_change_in_production_12345`. Même après suppression et commit ultérieur, la valeur reste dans l'historique Git.

**Procédure avec BFG Repo Cleaner** :

```bash
# 1. Créer un fichier listant les textes à remplacer
echo "dev_secret_key_change_in_production_12345" > passwords.txt
echo "postgres_hacked_password" >> passwords.txt

# 2. Lancer BFG pour nettoyer tout l'historique
java -jar bfg.jar --replace-text passwords.txt

# 3. Expirer le reflog et supprimer les objets orphelins
git reflog expire --expire=now --all
git gc --prune=now --force

# 4. Forcer la mise à jour du dépôt distant
git push --force --all
git push --force --tags
```

> **⚠️ Attention** : BFG réécrit l'historique Git. Après opération, toutes les branches et tags locaux doivent être nettoyés, et le dépôt distant doit être réinitialisé avec `git push --force`. Les autres contributeurs doivent recloner le dépôt.

**Vérification** :

```bash
# S'assurer qu'aucun secret ne subsiste dans l'arbre Git
git grep -nE "(api[_-]?key|password|secret|token)" -- . ":(exclude).env.example"
```

**Bonnes pratiques post-nettoyage** :

- Ajouter un script `pre-commit` qui bloque les futurs commits contenant des motifs de secrets.
- Utiliser `git-secrets` (AWS) ou `truffleHog` pour détecter les surprises.
- Documenter dans le `README.md` la procédure à suivre si un secret est accidentally commité.

#### 3.2.2. `python-dotenv` — Charger la configuration proprement

`python-dotenv` lit les variables depuis un fichier `.env` et les injecte dans `os.environ`. L'application n'a plus qu'à les lire avec `os.environ.get()`.

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Lit le fichier .env du répertoire courant

DATABASE_URL = os.environ.get("DATABASE_URL")
SECRET_KEY = os.environ.get("SECRET_KEY")
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "fake")  # Valeur par défaut sûre
```

**Fichier `.env.example` — Le modèle** :

Le fichier `.env.example` contient les **noms** des variables avec des **valeurs fictives**. Il est versionné dans Git car il guide les développeurs sur la configuration nécessaire, sans jamais contenir de vraie valeur.

```env
# .env.example — Exemple de configuration (valeurs fictives)
DATABASE_URL=postgresql://user:password@db:5432/music_hall
SECRET_KEY=replace-me-with-a-random-32-char-string
LLM_PROVIDER=fake
OPENAI_API_KEY=replace-with-your-openai-key
OLLAMA_BASE_URL=http://localhost:11434
```

**En production** : les variables proviennent de l'environnement du système ou du conteneur (Docker secrets, Kubernetes secrets, Vault). Le fichier `.env` n'est jamais utilisé en production.

> **Piège à éviter** : Ne jamais mettre de vraie clé API dans un exemple de README, même dans un dépôt privé. Les moteurs de recherche indexent ces fichiers et les clés ainsi exposées sont exploitées en quelques heures.

#### 3.2.3. Configuration Docker sans secret dans l'image

Le `Dockerfile` est un modèle d'image qui peut être partagé, stocké dans un registre et conservé longtemps. **Il ne doit contenir aucune valeur secrète.**

```dockerfile
# ❌ INTERDIT — La clé est figée dans l'image pour toujours
ENV SECRET_KEY="abc123-secret-key-do-not-commit"

# ✅ CORRECT — La clé est injectée au démarrage du conteneur
# via compose.yaml : env_file ou environment
```

Dans `compose.yaml`, la configuration se fait par injection au runtime :

```yaml
services:
  web:
    env_file:
      - .env          # Lecture locale (développement)
    secrets:
      - secret_key     # Montage Docker secret (production)
    environment:
      - SECRET_KEY_FILE=/run/secrets/secret_key
    read_only: true    # Filesystem en lecture seule
```

---

### 3.3. 10h30–11h30 — Fil rouge · Jalon 5 (60 min)

> **Objectif** : Valider strictement les entrées et isoler complètement les secrets dans les conteneurs.

#### 3.3.1. Validation stricte des entrées

Toute donnée reçue par l'API — corps JSON, paramètre d'URL, en-tête, fichier uploadé, variable d'environnement — doit être **validée avant traitement**.

**Les quatre niveaux de validation** :

1. **Type** : un identifiant doit être un entier, pas une chaîne. FastAPI y contribue via les convertisseurs de route (`<int:user_id>`).
2. **Format** : un email doit correspondre au format `x@y.z`. Pydantic valide avec `EmailStr`.
3. **Longueur** : un message de log ne doit pas dépasser 4096 caractères pour éviter l'épuisement mémoire.
4. **Valeurs autorisées (liste blanche)** : le niveau d'un log doit être parmi `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. Tout le reste est rejeté.

**Exemple avec Pydantic (FastAPI)** :

```python
from pydantic import BaseModel, Field, EmailStr
from typing import Literal

class LogCreate(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    source: str = Field(max_length=100)
    message: str = Field(max_length=4096, min_length=1)
    metadata: dict | None = None
```

> **Liste blanche vs liste noire** : une **liste blanche** accepte uniquement les valeurs prévues. Une **liste noire** tente de bloquer les valeurs dangereuses. La liste blanche est toujours préférable : il est impossible de lister toutes les valeurs dangereuses, mais on peut définir précisément ce qui est autorisé.

**Validation dans la route** :

```python
@app.post("/logs", status_code=201)
def create_log(log: LogCreate):  # Pydantic valide automatiquement
    # Ici, log.message a au plus 4096 caractères
    # log.level est forcément un niveau autorisé
    # log.source a au plus 100 caractères
    ...
```

Si les données ne respectent pas le contrat, FastAPI retourne automatiquement une réponse `422 Unprocessable Entity` avec un message précis indiquant quel champ est invalide et pourquoi.

**Validation au-delà de Pydantic** :

- Contraintes métier : `user_id <= 0` → `400 Bad Request`.
- Dépendances entre champs : si `source="database"`, alors `level` doit être au moins `WARNING`.
- Taille du corps entier : middleware limitant à 10 Mo.

#### 3.3.2. Isoler les secrets dans les conteneurs

Un conteneur doit recevoir sa configuration **à l'exécution**, jamais ne doit embarquer de secrets dans son image, et doit tourner avec le **minimum de privilèges** nécessaires.

**Principes appliqués dans notre architecture** :

| Mesure | Objectif | Implémentation |
|--------|----------|----------------|
| Utilisateur non-root | Empêcher l'exécution de commandes système en tant que root | `USER appuser` (UID 1000) dans le Dockerfile |
| Filesystem lecture seule | Empêcher l'écriture de fichiers malveillants | `read_only: true` dans compose.yaml |
| Répertoires écritables contrôlés | Permettre les écritures nécessaires (tmp, uploads) | `tmpfs: [/tmp, /var/tmp]` |
| Suppression de privilèges | Bloquer l'élévation de privilèges | `security_opt: [no-new-privileges:true]` et `cap_drop: [ALL]` |
| Secrets montés en fichiers | Ne pas passer les secrets en variable d'environnement (visibles via `/proc`) | Docker secrets dans `secrets:` et `env_file` |
| Pas de secret dans l'image | Empêcher la fuite via le registre | Aucun `ENV` contenant une valeur secrète dans le Dockerfile |

**Vérification finale** :

```bash
# Vérifier qu'aucun secret ne figure dans l'image
docker run --rm music-hall:latest grep -r "SECRET_KEY\|password\|api_key" /app || echo "Aucun secret trouvé"

# Vérifier que .gitignore couvre bien .env
git check-ignore -v .env

# Rechercher des secrets dans tout l'historique Git
git grep -nE "(api[_-]?key|password|secret|token)" -- . ":(exclude).env.example"
```

---

### 3.4. 11h30–12h00 — Bilan Semaine 1 (30 min)

> **Objectif** : Valider les acquis et ajuster les objectifs avant le week-end.

#### Bilan des acquis de la semaine 1

| Compétence | Statut |
|------------|--------|
| Cloner un dépôt, créer des branches, ouuvrir des Pull Requests | ✅ |
| Navigation Linux, scripting Bash, permissions | ✅ |
| Docker : Dockerfile, conteneur, compose multi-services | ✅ |
| Python : parsing JSON/CSV, fonctions, gestion d'erreurs | ✅ |
| OWASP Top 10, surface d'attaque, audit CTF | ✅ |
| **Secure Coding, validation des entrées** | ✅ |
| **Isolation des secrets (.env, .gitignore, dotenv)** | ✅ |
| **Durcissement conteneur (non-root, read-only, cap_drop)** | ✅ |

#### Acquis clés du Jalon 5

- [x] Validation stricte des entrées (type, format, longueur, liste blanche)
- [x] `.env.example` documenté avec des valeurs fictives
- [x] `.gitignore` vérifié et complet
- [x] Configuration Docker sans secret dans l'image
- [x] Secrets injectés au runtime (env_file, Docker secrets)
- [x] Conteneur exécuté en non-root avec filesystem read-only
- [x] Recherche de secrets dans l'arbre Git (`git grep`)

#### Ajustements pour le week-end

- Relire le contrat API minimal (endpoints `/health`, `/logs`, `/alerts`, `/logs/{id}/analyze`).
- Vérifier que les tests automatisés passent avec `LLM_PROVIDER=fake`.
- S'assurer que le démarrage `docker compose up --build` fonctionne sur les deux machines du binôme.

---

## 4. Concepts clés expliqués simplement

### 4.1. Secure Coding

**Définition** : Pratique d'écriture de code conçue pour résister aux attaques, en anticipant les entrées malveillantes ou malformées à chaque point de contact avec des données externes.

**Principes fondamentaux** :

- **Ne jamais faire confiance aux entrées** : tout vient de l'extérieur, tout peut être malveillant.
- **Échapper les sorties** : tout ce qui est affiché doit être protégé contre l'interprétation (HTML, SQL, JavaScript).
- **Utiliser des outils sûrs** : requêtes préparées, bibliothèques de hachage reconnues, validateurs de schéma.
- **Réduire la surface d'attaque** : moins il y a de points d'entrée, moins il y a de risques.

### 4.2. DevSecOps

**Définition** : Culture, pratiques et outils qui intègrent la sécurité dans chaque phase du développement logiciel, de la conception à la production.

```
Conception → Développement → Tests → Déploiement → Production
   ↕              ↕             ↕          ↕              ↕
 Audit        SAST/SCA      Tests      Scan image     Monitoring
 menaces     dépendances   de vuln.   CI/CD          & alertes
```

- **Shift-left** : déplacer les vérifications de sécurité vers le début du cycle.
- **Shift-right** : ajouter la surveillance en production (logs, alertes, réponses automatiques).
- **Automatisation** : les contrôles de sécurité s'exécutent sans intervention humaine dans le pipeline.

### 4.3. Secret vs Configuration

| | Secret | Configuration |
|---|---|---|
| **Définition** | Valeur qui doit rester privée | Valeur qui varie selon l'environnement |
| **Exemples** | Clé API, mot de passe de base de données, certificat TLS | URL de base, port, nom de service, mode de log |
| **Protection** | Stricte : .gitignore, secrets Docker, Vault | Variable d'environnement, fichier de config versionné |
| **Peut être dans Git ?** | **Jamais** | **Oui** (sauf si elle contient un secret) |

### 4.4. Liste blanche

**Définition** : Règle qui n'accepte que les valeurs explicitement prévues.

**Exemple** : Le niveau d'un log ne peut être que `DEBUG`, `INFO`, `WARNING`, `ERROR` ou `CRITICAL`. Tout autre valeur est rejetée.

```python
# Liste blanche avec Pydantic
level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# ❌ "INFO; DROP TABLE logs; --" → Rejeté automatiquement
# ❌ "HACK" → Rejeté automatiquement
# ✅ "ERROR" → Accepté
```

**Avantage** : simplicité et sécurité absolue. On ne cherche pas à deviner toutes les attaques possibles : on définit ce qui est légitime et tout le reste est refusé.

### 4.5. Journalisation (Logging)

**Définition** : Messages écrits par l'application pour expliquer ce qui se passe pendant son exécution.

**Règle d'or** : les journaux ne doivent **jamais** contenir de secrets.

```python
# ❌ INTERDIT — Le journal expose le token
logger.info(f"Requête envoyée avec token: {api_key}")

# ✅ CORRECT — On logue l'action, pas la donnée sensible
logger.info("Requête envoyée au fournisseur IA [provider=openai]")
```

**Bonnes pratiques** :

- Niveau `INFO` pour les actions normales, `WARNING` pour les anomalies, `ERROR` pour les échecs.
- Structurer les logs en JSON pour faciliter le parsing par les outils de monitoring.
- Masquer les données sensibles avant toute écriture (sanitisation).

### 4.6. Moindre privilège

**Définition** : Un programme ne doit disposer que des droits strictement nécessaires à sa tâche.

**Application dans Docker** :

- L'utilisateur `appuser` (UID 1000) ne peut pas installer de logiciels ni modifier la configuration système.
- Le filesystem en lecture seule empêche toute écriture malveillante.
- `cap_drop: ALL` supprime toutes les capacités Linux excessives.
- `no-new-privileges:true` empêche l'élévation de privilèges même en cas de compromise.

> **Analogie** : un comptable n'a pas besoin des clés du bureau. Il a accès au coffre (la base de données) et à son bureau (son répertoire de travail). Rien d'autre.

---

## 5. Livrables attendus — Jalon 5

| Livrable | Description | Critère de validation |
|----------|-------------|----------------------|
| **Validation stricte des entrées** | Toutes les routes API rejettent les entrées malformées (type, format, longueur, valeurs autorisées) | Une entrée trop longue ou mal formée est rejetée avec un code 400 ou 422 |
| **`.env.example` documenté** | Fichier avec les noms de variables et valeurs fictives, commenté | Un nouveau membre peut configurer le projet en lisant uniquement ce fichier |
| **`.gitignore` vérifié** | `.env`, `.env.production`, `secrets/` et autres données sensibles sont exclus de Git | `git check-ignore -v .env` retourne `.gitignore` |
| **Configuration Docker sans secret** | Le Dockerfile ne contient aucune valeur secrète ; la configuration est injectée au runtime | `docker compose config` ne révèle aucun secret ; `grep` dans l'image ne trouve rien |

**Commandes de vérification du Jalon 5** :

```bash
# 1. Pas de secrets dans le code
git grep -nE "(api[_-]?key|password|secret|token)" -- . ":(exclude).env.example"

# 2. .gitignore est correct
git check-ignore -v .env
git check-ignore -v secrets/

# 3. Docker Compose est cohérent
docker compose config

# 4. L'image ne contient pas de secrets
docker build -t test-image .
docker run --rm test-image grep -r "SECRET_KEY\|password\|api_key" /app || echo "OK"

# 5. L'API rejette les entrées invalides
curl -X POST http://localhost:5000/logs \
  -H "Content-Type: application/json" \
  -d '{"level":"INVALID","message":"x","source":"y"}'
# → 422 (le niveau n'est pas dans la liste blanche)
```

---

## 6. Erreurs fréquentes et comment les éviter

### 6.1. Erreurs de sécurité

| Erreur | Conséquence | Correction |
|--------|-------------|------------|
| Utiliser une clé API dans un exemple README | La clé est indexée par les moteurs de recherche et exploitée en quelques heures | Utiliser `YOUR_API_KEY_HERE` ou un placeholder textuel, jamais une clé valide |
| Journaliser tout le corps d'une requête | Les secrets contenus dans le corps (mots de passe, tokens) apparaissent dans les logs | Journaliser uniquement les métadonnées (méthode, URL, code de retour) ; sanitiser le corps avant écriture |
| Valider uniquement dans le navigateur | Une requête HTTP directe (curl, Postman) contourne toute validation JavaScript | Valider **côté serveur**, systématiquement, avec Pydantic ou équivalent |
| Stocker des secrets dans le code source | Toute personne ayant accès au dépôt y a accès | Utiliser `.env` (dev), secrets Docker (prod), Vault (prod avancé) |
| Utiliser une liste noire pour les entrées | Impossible de lister toutes les valeurs dangereuses | Utiliser une **liste blanche** : définir ce qui est autorisé |
| Hacher avec MD5 ou SHA-1 | Les mots de passe sont craqués en millisecondes | Utiliser bcrypt ou argon2 |
| Passer les secrets en variable d'environnement dans `environment:` | Les variables sont visibles via `/proc/<pid>/environ` dans le conteneur | Utiliser Docker secrets (fichiers montés dans `/run/secrets/`) |
| Laisser l'utilisateur root dans le conteneur | Un pirate qui compromet l'appli obtient les droits root | Définir `USER appuser` dans le Dockerfile |

### 6.2. Erreurs de configuration

| Erreur | Conséquence | Correction |
|--------|-------------|------------|
| `.env` non ajouté à `.gitignore` | Secrets versionnés et partagés | Vérifier avec `git check-ignore -v .env` |
| `.env.example` contient de vrais secrets | Le modèle expose des valeurs privées | Utiliser uniquement des valeurs fictives : `password`, `replace-me`, etc. |
| `git rm` sans `git commit` après suppression d'un fichier | Le fichier reste dans l'historique | Après suppression : `git add -A && git commit -m "remove sensitive file"` |
| Oublier de nettoyer l'historique après un commit accidentel | Le secret reste accessible via `git log -p` | Utiliser BFG ou `git filter-repo`, puis expirer le reflog |
| Hardcoder des valeurs dans le Dockerfile | L'image fuit la configuration | Utiliser `env_file` ou `secrets` dans compose.yaml |

### 6.3. Erreurs de validation

| Erreur | Conséquence | Correction |
|--------|-------------|------------|
| Accepter un `message` sans limite de longueur | Un payload de 500 Mo fait planter le serveur | `Field(max_length=4096)` + middleware de taille de requête |
| Accepter un `source` avec des caractères arbitraires | Injection dans les requêtes SQL ou les rapports IA | Valider avec une regex ou une liste blanche de sources |
| Ne pas valider les types | `"42"` (chaîne) au lieu de `42` (entier) provoque des erreurs inattendues | Laisser Pydantic typer fortement chaque champ |
| Supposer que le JSON est valide simplement parce qu'il est syntaxiquement correct | Des champs obligatoires peuvent être absents | Utiliser `Field(..., ...)` pour les champs requis dans Pydantic |

---

## 7. Connexions avec les jours suivants

### Transition vers la semaine 2

La semaine 1 s'achève sur la sécurisation de l'application. La semaine 2 s'appuie directement sur ces fondations :

#### Jour 6 — Lundi 14 septembre : Bases de données SQL & persistance

**Ce que le Jalon 5 rend possible** : Les entrées sont validées avant stockage. Les logs insérés en base sont garantis conformes au schéma (type, format, longueur). Les secrets de connexion à PostgreSQL (`DATABASE_URL`, `POSTGRES_PASSWORD`) sont isolés dans des secrets Docker, pas dans le code.

**Le lien** : La validation des entrées (jour 5) empêche les données corrompues ou malveillantes d'arriver dans les tables `logs` et `analyses` (jour 6). La persistance des données ne prend son sens que si les données sont fiables.

> **Piège évité** : Sans validation stricte, un log malformé peut corrompre une requête SQL ou inonder la base avec des données inutiles.

#### Jour 7 — Mardi 15 septembre : Intégration de l'IA & APIs REST

**Ce que le Jalon 5 rend possible** : Le message du log est nettoyé (sanitiser les PII, IPs, tokens) avant d'être envoyé à un fournisseur IA. La taille est limitée pour ne pas dépasser les quotas API. Le niveau est validé pour que l'IA reçoive un contexte cohérent.

**Le lien** : Envoyer un log non validé à un LLM peut révéler des secrets (fuite de données), produire des analyses aberrantes (prompt injection via les métadonnées du log), ou dépasser les limites de tokens du modèle.

> **Piège évité** : Journaliser et transmettre intégralement des données sensibles. Le sanitizer implémenté le jour 5 (`sanitize_log_message()`) est la protection principale.

#### Jours 8-10 — Sprint de développement & Demo Day

**Ce que le Jalon 5 rend possible** : Le projet démarre avec une base sécurisée. Les tests automatisés peuvent s'appuyer sur des entrées contrôlées. Le conteneur est durci pour la démonstration.

**Le lien** : La Demo Day nécessite un démarrage fiable (`docker compose up --build`), des tests qui passent (`pytest`), et une démonstration sans mauvaise surprise. Si la sécurisation n'est pas au point, la démo peut échouer à cause d'une fuite de secret, d'une entrée non validée ou d'un conteneur qui ne démarre pas.

> **Règle** : Ne **jamais** modifier le cœur du projet la veille de la démonstration sans rejouer tous les tests.

---

## 8. Pour aller plus loin — Conseils pratiques

### 8.1. Conseils pour la sécurisation au quotidien

- **Prenez l'habitude de chercher des secrets** : avant chaque commit, exécutez `git grep -nE "(api[_-]?key|password|secret|token)" -- .` pour vérifier que rien n'a glissé.
- **Utilisez des outils de scanning automatique** : installez `truffleHog` ou `gitleaks` comme pre-commit hook pour bloquer les commits contenant des secrets.
- **Générez des secrets aléatoires** : utilisez `openssl rand -hex 32` ou `python -c "import secrets; print(secrets.token_hex(32))"` plutôt que des valeurs choisies manuellement.
- **Testez votre `.gitignore`** : créez un fichier temporaire `.env.test`, tentez de le commiter, et vérifiez que Git le refuse.
- **Lisez les rapports Trivy et Snyk** : ne vous contentez pas de savoir que le scan fonctionne. Examinez les vulnérabilités trouvées et comprenez pourquoi elles sont classées ainsi.

### 8.2. Conseils pour la validation des entrées

- **Définissez le contrat de chaque endpoint avant de coder** : quel type, quelle longueur, quelles valeurs autorisées ? Documentez-le dans le schéma Pydantic.
- **Testez les limites** : envoyez une requête avec `message` de 4097 caractères, avec un `level` en minuscules, avec un `source` contenant des caractères spéciaux. Vérifiez que chaque cas est rejeté proprement.
- **Les messages d'erreur ne doivent pas fuiter la structure interne** : préférez `"level: valeur non autorisée"` à `"ValueError: invalid literal for ..."` qui révèle les noms de champs et la logique interne.

### 8.3. Conseils pour la gestion des secrets

- **Rotation** : en production, changez les secrets régulièrement et automatiquement. Un secret qui ne change jamais est un risque permanent.
- **Diffusion** : un secret ne doit être connu que de celui qui en a besoin. Ne le partagez jamais par message, email ou canal de discussion.
- **Documentation** : le `.env.example` doit expliquer chaque variable : son rôle, son format attendu, et qui la fournit (dev, ops, Vault, etc.).

### 8.4. Outils recommandés pour approfondir

| Outil | Usage | Installation |
|-------|-------|-------------|
| **truffleHog** | Détecter les secrets dans l'historique Git | `pip install trufflehog` |
| **gitleaks** | Alternative à truffleHog, plus rapide | `brew install gitleaks` ou binaire GitHub |
| **Trivy** | Scan de vulnérabilités d'images Docker | `npm install -g trivy` ou binaire |
| **Snyk** | Scan de dépendances et code | `npm install -g snyk` |
| **BFG Repo Cleaner** | Nettoyage de dépôts avec secrets | `java -jar bfg.jar` |
| **git-secrets** | Pre-commit hook anti-secrets | `apt install git-secrets` |
| **mkcert** | Certificats TLS locaux de confiance | `brew install mkcert` |

### 8.5. Récapitulatif des commandes essentielles du Jalon 5

```bash
# Vérifier .gitignore
git check-ignore -v .env
git check-ignore -v secrets/

# Chercher des secrets dans le code et l'historique
git grep -nE "(api[_-]?key|password|secret|token)" -- . ":(exclude).env.example"

# Vérifier la configuration Docker
docker compose config

# Vérifier l'image Docker ne contient pas de secrets
docker build -t check-image . && docker run --rm check-image sh -c "grep -rE 'SECRET|password|api_key' /app || echo 'AUCUN SECRET TROUVE'"

# Tester la validation des entrées
curl -X POST http://localhost:5000/logs \
  -H "Content-Type: application/json" \
  -d '{"level":"INVALID","message":"test","source":"test"}'
# Attendre : 422 Unprocessable Entity

# Tester le contournement navigateur (validation serveur)
curl -X POST http://localhost:5000/logs \
  -H "Content-Type: application/json" \
  -d '{"level":"INFO","message":"","source":"test"}'
# Attendre : 422 (message vide rejeté)

# Vérifier la taille maximale du corps
curl -X POST http://localhost:5000/logs \
  -H "Content-Type: application/json" \
  -d "$(python -c "print('{\"level\":\"ERROR\",\"message\":\"' + 'x'*5000000 + '\"}')")"
# Attendre : 413 Payload Too Large
```

---

## 9. Synthèse du Jour 5

Ce jour a posé les fondations de sécurité de l'ensemble du projet. Chaque concept appris ici se révélera critique dans les jours suivants :

- La **validation stricte** garantit que PostgreSQL ne recevra que des données conformes (jour 6).
- Le **sanitizer de logs** assure que l'IA ne recevra pas de données sensibles (jour 7).
- Le **conteneur durci** et la **configuration externalisée** assurent que la démonstration sera fiable et professionnelle (jours 8-10).

> **À retenir** : la sécurité n'est pas une fonctionnalité ajoutée à la fin. C'est une manière de concevoir, coder et déployer qui commence avec la première ligne de code et ne s'arrête jamais.

---

*Fin du document — Jour 5 (Vendredi 11 septembre) — Semaine 1*
