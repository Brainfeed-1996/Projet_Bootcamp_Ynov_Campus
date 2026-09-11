# Explications — Semaine 1 DevSecOps

## 1. Sécurisation & Clean Code (09h00–09h40)

### Secure Coding
- **Principe** : écrire du code qui résiste aux attaques courantes (injection, XSS, overflow, etc.).
- **Exemple** : valider et échapper les entrées utilisateur, utiliser des requêtes préparées, limiter les permissions.

### Principes DevSecOps
- Intégrer la sécurité dans le pipeline CI/CD (SAST, tests de vulnérabilités, analyse statique).
- **Shift-left** : détecter les problèmes tôt, moins cher et plus rapide à corriger.
- **Shift-right** : monitorer en production (logs, alertes, réponses automatiques).

### Isoler les secrets avec `.env` et `.gitignore`
- Les clés, mots de passe, tokens ne doivent **jamais** être dans le code source.
- Utiliser un fichier `.env` (local) ou un secret manager (Vault, AWS Secrets Manager, etc.).
- `.gitignore` contient `.env` pour empêcher le commit accidentel.

### Hachage (bcrypt/argon2) vs Chiffrement
| Concept | Utilisation | Exemple |
|---------|-------------|---------|
| **Hachage** | Stocker les mots de passe (irréversible, salé) | `bcrypt.hashpw(password, salt)` |
| **Chiffrement** | Données reutilisables (reversible avec clé) | AES, TLS |

> **Règle d'or** : on hache les mots de passe, on chiffre les données sensibles.

---

## 2. Hardening & variables d'environnement (09h40–10h30)

### Nettoyer un dépôt avec BFG
Si des clés ou mots de passe ont été commités dans l'historique :

```bash
# 1. Créer un fichier contenant les mots de passe à remplacer
echo "dev_secret_key_change_in_production_12345" > passwords.txt

# 2. Lancer BFG pour remplacer le texte dans tout l'historique
java -jar bfg.jar --replace-text passwords.txt

# 3. Expirer le reflog et nettoyer les objets orphelins
git reflog expire --expire=now --all && git gc --prune=now --force
```

> **Important** : BFG réécrit l'historique. Toutes les branches et tags doivent être supprimés localement avant, et le dépôt distant doit être réinitialisé (`git push --force`).

### python-dotenv
- Lit les variables depuis `.env` et les injecte dans `os.environ`.
- En production, on utilise les variables d'environnement du système ou du conteneur (Docker, Kubernetes).

### `.env` dans `compose.yaml`
```yaml
env_file:
  - .env
```
- Le conteneur lit le `.env` au démarrage.
- `read_only: true` rend le filesystem en lecture-seule pour limiter les écritures malveillantes.

---

## 3. Fil rouge · Jalon 5 (10h30–11h30)

### Valider strictement les entrées
- Utiliser des convertisseurs de type Flask (`<int:user_id>`) pour valider le format.
- Ajouter des contraintes logiques (ex: `user_id <= 0` → 400).
- Échapper les sorties (HTML, JSON) pour éviter les XSS.
- Utiliser des schémas de validation (Pydantic, marshmallow) pour les APIs.

### Isoler les secrets dans les conteneurs
- **Dockerfile** : ne pas copier `.env`, ne pas hardcoder les clés.
- **compose.yaml** : utiliser `env_file` ou `environment` pour injecter les variables.
- **Dockerfile** actuel :
  ```dockerfile
  USER appuser  # Exécuter en non-root
  ```
- **compose.yaml** actuel :
  ```yaml
  read_only: true
  tmpfs:
    - /tmp
  ```
  → Le filesystem est en lecture-seule, `/tmp` est montre en tmpfs (mémoire volatile).

---

## 4. Bilan Semaine 1 (11h30–12h00)

### Acquis
- [x] Isoler les secrets (`.env`, `.gitignore`)
- [x] Distinguer hachage et chiffrement
- [x] Nettoyer un dépôt avec BFG
- [x] Utiliser `python-dotenv`
- [x] Valider les entrées (`<int:user_id>`, contraintes logiques)
- [x] Durcir un conteneur Docker (`USER`, `read_only`, `tmpfs`)

### Correction des erreurs Docker

#### Erreur 1 : `ImportError: cannot import name 're' from 'flask'`
- **Cause** : `from flask import Flask, request, abort, re` — `re` n'existe pas dans le module `flask`, c'est un module standard Python.
- **Correction** : importer `re` séparément :
  ```python
  import re
  from flask import Flask, request, abort
  ```

#### Erreur 2 : Le conteneur s'arrêtait immédiatement
- **Cause** : Le script Python ne démarrait pas le serveur Flask (pas de `app.run()`).
- **Correction** : Ajouter un bloc `if __name__ == "__main__":` avec `app.run(host="0.0.0.0", port=5000, debug=False)`.

#### Erreur 3 : `compose.yaml` — attribut `version` obsolète
- **Message** : "the attribute `version` is obsolete, it will be ignored"
- **Correction** : Supprimer la ligne `version: '3.8'` (les versions de Compose sont héritées de l'outil).

#### Résultat
- Conteneur actif sur `http://localhost:5000`
- `/api/users/42` → `200 {"id":42}`
- `/api/users/0` → `400 ID utilisateur invalide.`

### À améliorer / poursuivre
- [x] Ajouter un `requirements.txt` → créé avec `flask`, `python-dotenv`, `pytest`, `psycopg2-binary`, `sqlalchemy`, `bcrypt`
- [x] Ajouter des tests unitaires (pytest) → `test_app.py` couvre les cas valides et invalides
- [x] Ajouter un `.dockerignore` → évite de copier `.env`, `.git`, `__pycache__`, etc.
- [x] Migration PostgreSQL avec volume persistant, healthcheck, `DATABASE_URL`
- [x] Table `users` avec hachage bcrypt des mots de passe
- [ ] Ajouter un scan de vulnérabilités (Snyk, Trivy) dans le CI
- [ ] Utiliser un gestionnaire de secrets (Vault, AWS Secrets Manager) en production

---

## 5. PostgreSQL & Base de données

### Livrables attendus
- Tables `users`, `logs` et `analyses` créées automatiquement au démarrage
- Connexion via `DATABASE_URL` (variable d'environnement)
- Volume persistant `postgres_data` pour que les données survivent aux redémarrages
- Filtres GET `/logs` (level, source, limit)
- Requêtes SQL avec paramètres (text() + params), jamais de concaténation
- Mots de passe hachés avec bcrypt (scrypt par Werkzeug)

### Architecture Docker Compose
```yaml
services:
  web:
    build: .
    depends_on:
      db:
        condition: service_healthy
    read_only: true
    tmpfs:
      - /tmp

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: appppassword
      POSTGRES_DB: music_hall
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d music_hall"]
      interval: 5s
      timeout: 5s
      retries: 10

volumes:
  postgres_data:
```

### Schéma de la table `users`
| Colonne | Type | Contraintes |
|---------|------|-------------|
| `id` | INTEGER | PK, autoincrement |
| `username` | VARCHAR(50) | NOT NULL, UNIQUE |
| `email` | VARCHAR(120) | NOT NULL, UNIQUE |
| `password_hash` | VARCHAR(256) | NOT NULL |
| `is_active` | BOOLEAN | DEFAULT true |
| `created_at` | TIMESTAMP | DEFAULT now() |

### Routes implémentées
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/users/<int:user_id>` | Valide l'ID (type + valeur > 0) |
| POST | `/users` | Crée un utilisateur (hachage bcrypt) |
| DELETE | `/users/<int:user_id>` | Soft delete (`is_active = false`) |
| GET | `/logs` | Filtres optionnels `level`, `source`, `limit` |
| POST | `/logs` | Création de log |
| GET | `/analyses` | Liste des analyses |
| POST | `/analyses` | Création d'analyse |
| GET | `/health` | Vérification de la connexion DB |

### Sécurité
- **Hachage** : `generate_password_hash()` / `check_password_hash()` (Werkzeug, scrypt)
- **unicité** : vérification avant insertion (username/email) → 409 si existant
- **Soft delete** : suppression logique pour traçabilité
- **Paramètres SQL** : toutes les requêtes utilisent `text()` avec paramètres nommés
- **Validation** : `<int:user_id>` + contrainte `user_id <= 0` → 400

### Tests effectués
| Endpoint | Test | Résultat |
|----------|------|----------|
| `GET /api/users/42` | ID valide | `200 {"id":42}` |
| `GET /health` | Santé DB | `200 {"database":"up","status":"ok"}` |
| `POST /users` | Création user | `201 {"id":1,"username":"testuser","status":"created"}` |
| `POST /users` | Doublon username/email | `409 Conflict` |
| `SELECT * FROM users` | Vérification DB | `password_hash` haché (scrypt) |
| `\dt` | Tables | `users`, `logs`, `analyses` |
| Redémarrage complet | Persistance | Données intactes |

#### Scan de vulnérabilités (Snyk / Trivy)
- **Snyk** : analyse les dépendances (npm, pip, etc.) et trouve les vulnérabilités connues.
  ```bash
  npm install -g snyk
  snyk auth <token>
  snyk test
  ```
- **Trivy** : scan d'images Docker et de dépôts Git.
  ```bash
  trivy image mon-image:latest
  ```
- Dans un pipeline CI (GitHub Actions, GitLab CI) :
  ```yaml
  - name: Scan with Trivy
    uses: aquasecurity/trivy-action@master
    with:
      image-ref: mon-image:latest
  ```

#### Gestionnaire de secrets en production
- **Vault (HashiCorp)** : stocke, chiffre et contrôle l'accès aux secrets (clés API, mots de passe).
- **AWS Secrets Manager** : service géré par AWS, intégré à IAM.
- **Azure Key Vault** : équivalent Azure.
- **Google Secret Manager** : équivalent GCP.
- **Principe** : jamais de secrets dans le code, `.env` ou les conteneurs. On les injecte au runtime via des variables d'environnement ou des montages de secrets.