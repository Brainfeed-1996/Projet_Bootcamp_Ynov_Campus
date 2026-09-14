# Jour 1 — Lundi 7 septembre

## Des logs bruts à une alerte exploitable

### Semaine 1 · Socle systèmes, infrastructure et début du projet

---

> **À propos de ce document** : Ce fichier est un guide d'explication orale complet pour le Jour 1. Il est conçu pour être lu à voix haute devant le groupe. Chaque section est structurée pour faciliter la compréhension, avec des exemples concrets, des encadrés de conseil et des mises en garde.

---

## 1. Résumé exécutif du jour

Le Jour 1 pose les **fondations humaines, techniques et organisationnelles** du projet "Des logs bruts à une alerte exploitable". Ce jour est celui où le binôme se forme, où l'environnement de travail est installé, et où les premiers commits Git sont réalisés. Sans une installation réussie et un dépôt partagé, aucune avancée technique n'est possible les jours suivants.

En une matinée, les participants passeront de « zéro outil configuré » à « dépôt Git fonctionnel avec première Pull Request mergée ». Le projet final — une API FastAPI qui ingère des logs techniques, les stocke dans PostgreSQL, demande à un modèle d'IA une analyse structurée et expose le tout via Swagger UI — est complexe. Mais il repose sur des bases que nous installons aujourd'hui.

**Le fil rouge du projet** : un événement technique (log) entre dans l'API, est validé, persisté, puis analysé par une IA pour produire une alerte exploitable. Chaque outil installé aujourd'hui intervient dans ce parcours : Git pour versionner le code, Docker pour reproduire l'environnement, Python pour écrire l'API, et GitHub/GitLab pour collaborer.

---

## 2. Objectifs pédagogiques du jour

À l'issue de cette session, chaque binôme sera capable de :

- **Configurer un environnement de développement complet** (VS Code, Python, Git, Docker) sur sa machine
- **Expliquer le rôle de chaque outil** du projet et sa place dans l'architecture cible
- **Utiliser Git au quotidien** : cloner, créer une branche, committer, pousser et ouvrir une Pull Request
- **Collaborer via peer-programming** en binôme mixte (profil avancé + profil débutant)
- **Rédiger un README initial** et respecter les règles de base d'un dépôt professionnel

### Objectifs mesurables

| Objectif | Critère de réussite |
|----------|---------------------|
| Environnement opérationnel | `python --version`, `git --version`, `docker --version` fonctionnent dans le terminal |
| Dépôt partagé | Le dépôt est cloné sur les deux machines du binôme |
| Première PR | Une branche `docs/readme` est créée, poussée et fusionnée via Pull Request |
| README fonctionnel | Le fichier `README.md` existe, décrit le projet et contient les instructions de démarrage |

---

## 3. Détaillage horaire

### 3.1 · 09h00–09h30 — Accueil & test de positionnement

#### 09h00–09h10 · Présentation de l'organisation et des objectifs

L'intervenant commence par poser le cadre :

- **Durée du bootcamp** : 10 jours, 7 septembre au 18 septembre
- **Objectif global** : construire une API fonctionnelle qui transforme des logs bruts en alertes exploitables, démonstrée via Swagger UI
- **Évaluation** : Demo Day le vendredi 18 septembre (6 minutes de démo + 4 minutes de Q&A, parole répartie 50/50)

> **Encadré — Pourquoi ce jour est crucial**
> Le Jour 1 détermine la capacité du binôme à avancer autonome. Une machine mal configurée ou un dépôt inaccessible bloquent tout le reste. Les 30 premières minutes servent à identifier les profils pour adapter le rythme, puis à garantir que chaque machine est prête.

#### 09h10–09h30 · QCM individuel de positionnement

Chaque participant répond seul à un questionnaire à choix multiples pour cartographier ses niveaux :

- **Niveau terminal** : connaissez-vous les commandes Linux de base ?
- **Niveau Python** : savez-vous différencier une liste d'un dictionnaire ?
- **Niveau Git** : avez-vous déjà créé une branche ?
- **Niveau Docker** : connaissez-vous la différence entre une image et un conteneur ?

Le QCM ne note personne. Il sert à ajuster la pédagogie : si tout le monde est débutant en Docker, on ralentit le J03 ; si tout le monde connaît Git, on accélère le J01.

---

### 3.2 · 09h30–10h00 — Constitution des binômes & peer-programming

#### Formation des binômes

Les binômes sont **mixtes** : un profil avancé est associé à un profil débutant. L'objectif est la **pair programming** :

- **Le pilote (profil avancé)** : guide, explique, donne les grandes directions. Il ne tape pas à la place de l'autre.
- **Le copilote (profil débutant)** : garde le clavier, tape les commandes, pose les questions. C'est en tapant qu'on apprend.

> **Encadré — La règle du clavier**
> Le débutant tape. L'avancé observe et guide. Si le débutant bloque, l'avancé propose une approche verbale (« on essaie d'abord `git status` pour voir l'état »), puis laisse le débutant exécuter. Le rôle de l'avancé est de rendre le débutant autonome, pas de faire le travail à sa place.

#### Rotation prévue

Au fil des jours, les rôles peuvent alterner pour que chacun expérimente les deux positions. Aujourd'hui, le débutant tape lors des commandes Git et l'avancé guide la résolution de problèmes.

---

### 3.3 · 10h00–11h15 — Mise en place de l'environnement

Cette tranche est la plus dense techniquement. Elle couvre six installations critiques.

#### VS Code

- L'éditeur recommandé pour sa compatibilité avec les extensions Python, GitLens et Docker
- Installation de la [version officielle](https://code.visualstudio.com/)
- Extensions recommandées dès l'ouverture : **Python**, **GitLens**, **Docker**, **Pylance**

> **Conseil pour le binôme** : l'avancé aide le débutant à installer les extensions pendant que le débutant vérifie que VS Code se lance correctement.

#### Git

- Vérification : `git --version` (minimum 2.30 recommandé)
- Si absent : installation via le site officiel [git-scm.com](https://git-scm.com/)
- Configuration initiale obligatoire :
  ```bash
  git config --global user.name "Prénom Nom"
  git config --global user.email "email@exemple.com"
  ```
- Vérification : `git config --list`

#### Python 3.10+

- Vérification : `python --version` ou `python3 --version`
- Le projet requiert **Python 3.10 minimum** pour les *type hints* avancées (syntaxe `X | Y`)
- Si Windows : installer via [python.org](https://www.python.org/) en cochant **"Add Python to PATH"** — c'est le piège n°1
- Si WSL2 : `sudo apt update && sudo apt install python3 python3-pip`
- Vérification de pip : `pip --version`

> **Encadré — Le piège PATH sous Windows**
> Quand Python est installé sans la case "Add to PATH", la commande `python` n'est reconnue nulle part, même dans un terminal nouveau. Solution : réinstaller Python en cochant l'option, ou ajouter manuellement le chemin (`C:\Users\<utilisateur>\AppData\Local\Programs\Python\Python311`) aux variables d'environnement PATH.

#### Docker Desktop

- Installation depuis [docker.com](https://www.docker.com/products/docker-desktop/)
- Vérification après lancement : `docker --version` et `docker compose version`
- Sur Windows, Docker Desktop nécessite **WSL2** ou **Hyper-V**. S'assurer que le mode est activé dans les paramètres.
- Premier test : `docker run hello-world` doit afficher un message de succès.

#### Clés SSH et GitHub/GitLab

- Génération d'une clé SSH :
  ```bash
  ssh-keygen -t ed25519 -C "email@exemple.com"
  ```
- La clé publique (`~/.ssh/id_ed25519.pub`) est ajoutée dans les paramètres SSH du compte GitHub ou GitLab
- Test : `ssh -T git@github.com` doit retourner un message de bienvenue
- Ce mécanisme permet de pousser (push) et cloner sans re-saisir de mot de passe à chaque opération

#### WSL2 et variables PATH (si applicable)

- WSL2 permet d'exécuter Linux nativement sous Windows
- Installation : `wsl --install` dans un PowerShell administrateur, puis redémarrage
- Après installation, ouvrir Ubuntu et y installer Python, Git, Docker CLI
- Les variables PATH dans WSL2 se configurent dans `~/.bashrc` ou `~/.zshrc`

> **Piège fréquent** : les outils installés dans Windows (Python, Git) ne sont pas automatiquement accessibles dans WSL2. Il faut les installer aussi dans la distribution WSL, ou utiliser les binaires Windows depuis `/mnt/c/...`.

---

### 3.4 · 11h15–12h00 — Bases de Git & Jalon 1

#### Révision des commandes fondamentales

| Commande | Rôle | Exemple |
|----------|------|---------|
| `git clone` | Copier un dépôt distant | `git clone https://github.com/groupe/depot.git` |
| `git status` | Voir l'état des fichiers | Montre les fichiers modifiés, ajoutés ou supprimés |
| `git add` | Préparer des modifications | `git add README.md` |
| `git commit` | Photographier les modifications | `git commit -m "docs: initialise le projet"` |
| `git push` | Envoyer vers le dépôt distant | `git push -u origin docs/readme` |
| `git branch` | Lister ou créer des branches | `git switch -c docs/readme` |
| `git pull request` | Proposer une fusion | Via l'interface web GitHub/GitLab |

> **Principe fondamental** : `git status` est votre boussole. Avant chaque commande, regardez ce que Git voit réellement. S'il dit « nothing to commit », votre travail est déjà enregistré. S'il montre des fichiers rouges, ils sont modifiés et prêts à être ajoutés.

#### Jalon 1 en pratique — Dépôt et première Pull Request

**Étape 1 — Créer le dépôt officiel**

Un membre du binôme crée le dépôt sur GitHub ou GitLab (nom suggéré : `log-sentinel-api` ou selon la convention de l'organisme). L'autre clone immédiatement :

```bash
git clone https://github.com/groupe/log-sentinel-api.git
cd log-sentinel-api
```

**Étape 2 — Rédiger le README**

Le `README.md` est la carte de visite du dépôt. Il contient au minimum :

- Le nom du projet : Des logs bruts à une alerte exploitable
- Une phrase de description : « API FastAPI qui ingère des logs techniques, les stocke dans PostgreSQL et demande à un modèle IA une analyse structurée. »
- La stack technique : FastAPI, PostgreSQL, OpenAI/Ollama, Swagger UI, Docker
- Les instructions de démarrage (à enrichir progressivement)

```markdown
# Log Sentinel API

API FastAPI d'ingestion et d'analyse de logs sécurisée, conçue pour un cours DevSecOps.

## Stack
- Python 3.11+, FastAPI
- PostgreSQL
- OpenAI ou Ollama (moteur IA)
- Docker, Docker Compose
- Swagger UI (démonstration)
```

**Étape 3 — Première branche et commit**

```bash
git switch -c docs/readme
git add README.md .gitignore .env.example
git commit -m "docs: initialise le projet avec README, .gitignore et .env.example"
git push -u origin docs/readme
```

**Étape 4 — Pull Request**

Sur GitHub/GitLab, l'interface propose de créer une Pull Request depuis la branche `docs/readme` vers `main`. La PR est relue (par l'intervenant, un autre binôme ou selon la pédagogie), puis fusionnée.

> **Pourquoi la PR et pas un push direct sur main ?**
> Un push direct sur la branche principale bloque tout le binôme si une erreur est introduite. La Pull Request crée un **moment de relecture** : on vérifie que le changement est compréhensible, testable et documenté avant qu'il n'entre dans le code partagé. C'est un filet de sécurité collectif.

---

## 4. Concepts clés expliqués simplement

### 4.1 · Dépôt (Repository)

Un dépôt est le dossier de votre projet suivi par Git. Il existe **localement** (sur votre machine) et **distantement** (sur GitHub/GitLab). Chaque dépôt a un historique complet de toutes les modifications jamais effectuées.

**Analogie** : un dépôt est comme un journal de bord qui note chaque feuille modifiée, avec la date, l'auteur et le contenu exact de chaque changement.

### 4.2 · Commit

Un commit est une photographie nommée d'un petit ensemble de modifications cohérentes. Il ne faut pas faire un commit « final » qui mélange README, Docker, base de données et code API. Chaque commit doit répondre à une seule intention.

**Exemple de bons messages** :
- `docs: initialise le README`
- `feat: ajoute l'endpoint /health`
- `fix: corrige la connexion PostgreSQL`

**Règle** : le préfixe (docs, feat, fix) indique la nature du changement. Le message après les deux-points décrit précisément ce qui a été fait.

### 4.3 · Branche (Branch)

Une branche est une ligne de travail séparée où l'on peut avancer sans modifier la version principale (`main`). On crée une branche pour chaque tâche ou chaque fonctionnalité.

**Analogie** : imaginez un document Word. Au lieu de modifier le document original, vous faites une copie, modifiez la copie, et ne remplacez l'original que lorsque vous êtes sûr du résultat.

**Conventions de nommage** :
- `docs/readme` — documentation
- `feat/health-endpoint` — nouvelle fonctionnalité
- `fix/db-connection` — correction de bug

### 4.4 · Pull Request (PR)

Une Pull Request est une proposition de fusionner une branche dans la branche principale. Elle permet de :

- Comparer les différences ligne par ligne
- Discuter des changements
- Faire relire par au moins une personne
- Vérifier que les tests passent avant fusion

### 4.5 · .gitignore

Le fichier `.gitignore` liste les fichiers que Git ne doit jamais suivre. C'est **critique** pour la sécurité du projet :

```
# Secrets et configuration locale
.env
.env.production
secrets/

# Environnements virtuels et caches
__pycache__/
*.pyc
.venv/

# Bases de données
*.sqlite
*.db
postgres_data/

# Fichiers temporaires
*.tmp
*.log

# Fichiers IDE
.vscode/
.idea/
```

> **Règle d'or** : si vous avez commité un secret (clé API, mot de passe) par erreur, le supprimer du fichier ne suffit pas — il reste dans l'historique Git. Il faut utiliser des outils comme BFG Repo Cleaner pour purger l'historique. C'est pourquoi `.gitignore` se configure **avant** le premier commit.

### 4.6 · L'architecture du projet en une image

```
Fichiers JSON/CSV ou requêtes HTTP
        │
        ▼
┌─────────────────┐     Connexion SQL      ┌──────────────────┐
│   API FastAPI   │ ◄────────────────────► │   PostgreSQL     │
│  Validation,    │     (via DATABASE_URL)  │  Logs, analyses  │
│  ingestion      │                         │  et alertes      │
└────────┬────────┘                         └──────────────────┘
         │
         │ Demande d'analyse
         ▼
┌─────────────────┐
│ OpenAI ou       │
│ Ollama (IA)     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Swagger UI     │
│  (Démonstration)│
└─────────────────┘
```

### 4.7 · Connexion entre les outils

Chaque outil installé aujourd'hui a un rôle précis dans l'architecture :

| Outil | Rôle dans le projet | Quand on l'utilise |
|-------|---------------------|-------------------|
| **VS Code** | Écrire le code Python de l'API | Tous les jours |
| **Python** | Exécuter l'API, parser les logs, valider les données | Tous les jours |
| **Git** | Versionner le code, collaborer en binôme | Chaque session |
| **Docker** | Lancer PostgreSQL et l'API dans des conteneurs reproductibles | J03+ (installation aujourd'hui) |
| **GitHub/GitLab** | Héberger le dépôt, gérer les PR | J01+ |
| **Terminal** | Piloter tous les outils via des commandes | En permanence |

---

## 5. Livrables attendus — Jalon 1

| Livrable | Description | Critère de qualité |
|----------|-------------|-------------------|
| **Dépôt officiel** | URL du dépôt GitHub/GitLab du groupe | Accessible, vide, avec README |
| **README initial** | Présentation du projet, stack, objectifs | Claire, structurée, sans secret |
| **Branches de travail** | Au moins `docs/readme` créée et poussée | Nom descriptif, pas sur main |
| **Première PR** | Fusionnée après relecture | Message clair, relecture effectuée |
| **.gitignore** | Configuration initiale des fichiers ignorés | Contient .env, secrets, __pycache__ |
| **.env.example** | Modèle de configuration sans valeurs réelles | Aucune clé API, mot de passe ou secret |

### Definition of Done du Jalon 1

- [ ] Chaque membre sait cloner le dépôt (`git clone`)
- [ ] `git status` est propre après la fusion (aucun fichier non commité)
- [ ] Le README explique le but du projet « Des logs bruts à une alerte exploitable »
- [ ] La branche `docs/readme` a été fusionnée dans `main` via une Pull Request relue
- [ ] Aucun secret ne figure dans l'historique Git

---

## 6. Erreurs fréquentes et comment les éviter

### Erreur 1 — Travailler directement dans `main`

**Le problème** : un commit direct sur `main` y introduit du code non relu. Si une erreur est poussée, tout le binôme est bloqué.

**La solution** : toujours créer une branche avant de modifier quoi que ce soit :
```bash
git switch -c docs/readme
# travailler sur la branche
git push -u origin docs/readme
# puis fusionner via Pull Request
```

### Erreur 2 — Faire un commit « fourre-tout »

**Le problème** : un commit `feat: update` qui mélange README, Dockerfile, code Python et configuration. Impossible de comprendre ce qui a changé, impossible de revenir en arrière proprement.

**La solution** : un commit = une intention. Séparer les changements :
```bash
git add README.md
git commit -m "docs: initialise le README"

git add app.py
git commit -m "feat: ajoute l'endpoint /health"
```

### Erreur 3 — Ajouter un secret dans Git

**Le problème** : une clé API, un mot de passe ou un token dans le code ou `.env` commité. Même après suppression, la donnée reste dans l'historique et est accessible à quiconque a accès au dépôt.

**La solution** :
- Vérifier `.gitignore` avant le premier commit
- Utiliser `.env.example` avec des valeurs fictives
- Rechercher les secrets avant chaque push :
  ```bash
  git grep -nE "(api[_-]?key|password|secret)" -- . ":(exclude).env.example"
  ```
- Si un secret a été commité : ne pas l'ignorer, le purger avec BFG ou l'historique Git rewrite, et le faire supprimer côté serveur.

### Erreur 4 — Cloner avec un chemin absolu spécifique à sa machine

**Le problème** : un binôme clone dans `C:\Users\Scott_Adams\Projects\...` et l'autre ne peut pas reproduire le chemin.

**La solution** : toujours travailler depuis la racine du dépôt cloné, avec des chemins relatifs. Le `cd` initial dans le dossier du projet suffit.

### Erreur 5 — Ne pas lire `git status` avant de commander

**Le problème** : exécuter `git add` ou `git commit` sans savoir ce que Git voit mène à des commits involontaires (fichiers d'environnement, caches, etc.).

**La solution** : prendre le réflexe :
```bash
git status       # voir l'état
git diff         # voir les différences
git add ...      # préparer
git commit ...   # photographier
```

### Erreur 6 — Confondre `localhost` sur la machine et dans un conteneur Docker

**Le problème** : `localhost` dans le terminal désigne la machine hôte, mais `localhost` dans un conteneur Docker désigne le conteneur lui-même. L'API et PostgreSQL tournent dans des conteneurs séparés — ils ne partagent pas `localhost`.

**La solution** : dans `compose.yaml`, les services communiquent par nom de service (`db`, `web`) et non par `localhost`. Ce point sera approfondi au J06, mais il faut en être conscient dès aujourd'hui.

### Erreur 7 — Oublier de configurer SSH

**Le problème** : sans clé SSH, chaque `git push` ou `git pull` demande un mot de passe GitHub/GitLab, ce qui ralentit le travail et peut bloquer l'automatisation.

**La solution** : générer la clé SSH dès l'installation et l'ajouter dans les paramètres du compte. Tester avec `ssh -T git@github.com`.

---

## 7. Connexions avec les jours suivants

Le Jour 1 n'est pas isolé : chaque compétence acquise aujourd'hui est réutilisée et approfondie.

### Jour 2 (Mardi 8 septembre) — Linux, scripting Bash & réseau

- **Git** est utilisé pour récupérer les scripts Bash du groupe via `git pull`
- **Le terminal** (installé et testé aujourd'hui) est l'outil principal du J02
- **Le concept de variable d'environnement** abordé aujourd'hui sera utilisé pour configurer les scripts réseau

### Jour 3 (Mercredi 9 septembre) — Conteneurisation Docker & scripting Python

- **Docker** (installé aujourd'hui) sera mis en œuvre : `docker run`, `docker ps`, `docker compose up`
- **Python** (vérifié aujourd'hui) servira à parser les logs JSON/CSV et à écrire l'API
- **Le README** du J01 sera enrichi avec les instructions Docker

### Jour 4 (Jeudi 10 septembre) — Cyber offensive : sensibilisation & OWASP

- **La validation des entrées** prévue dans l'architecture (POST /logs) sera auditée
- **Git** servira à documenter les risques et les corrections via des issues et des PR de remédiation

### Jour 5 (Vendredi 11 septembre) — Cyber défensive & DevSecOps

- **`.gitignore`** et **`.env`** configurés aujourd'hui sont les fondations de l'isolation des secrets
- **Les branches** créées aujourd'hui portent les correctifs de sécurité
- **Le concept de moindre privilège** (découvert avec Docker) s'applique à l'application elle-même

### Jours 6-7 — Persistance PostgreSQL & Analyse IA

- **Le dépôt Git** partagé depuis le J01 sert de source unique de vérité pour le code de connexion à PostgreSQL et les adaptateurs IA
- **Les PR** permettent de faire relire les connexions bases de données et les appels IA avant leur fusion

### Jours 8-10 — Sprint, tests et Demo Day

- Tout le code écrit pendant le sprint s'appuie sur l'infrastructure Git et dépôt en place depuis le J01
- **Le README initial** du J01 est enrichi progressivement jusqu'à devenir le README final du Demo Day
- **Les branches** du J01 ont posé la convention de nommage utilisée pour tout le projet

> **Encadré — Le domino du J01**
> Si l'installation du J01 réussit, chaque jour suivant est possible. Si Docker n'est pas installé, le J03 est bloqué. Si Git n'est pas configuré, aucune collaboration n'est possible. Le Jour 1 est le socle sur lequel tout le projet repose.

---

## 8. Pour aller plus loin — Conseils pratiques

### Conseil 1 — Maîtriser `git status` avant tout

Le premier réflexe de tout développeur expérimenté est de taper `git status`. Ce seul geste prévient 80 % des erreurs Git : commits oubliés, fichiers dans la mauvaise branche, opérations sur une branche non à jour.

### Conseil 2 — Configurer `.gitignore` dès le clonage

Avant même de lire le code, regardez le `.gitignore` existant. S'il n'y en a pas, créez-en un immédiatement. C'est la meilleure habitude de sécurité en début de projet.

### Conseil 3 — Utiliser des branches même pour de petites modifications

Même pour corriger une faute de frappe dans le README, créez une branche. L'automatisation de la workflow (boutique de PR) ne vaut que si chaque contribution passe par elle.

### Conseil 4 — Tester le démarrage Docker tôt

Ne pas attendre le J03 pour vérifier que Docker fonctionne. Lancez un test simple dès aujourd'hui :
```bash
docker run --rm hello-world
```
Si cela échoue, résolvez-le maintenant — avant que tout le monde ne soit bloqué.

### Conseil 5 — Écrire le README en collaboratif

Le README est le premier point de contact de tout visiteur du dépôt. En binôme, le débutant rédige les sections descriptives et l'avancé vérifie la clarté et l'exhaustivité. C'est un excellent premier exercice de pair programming.

### Conseil 6 — Activer les webhooks et protections de branche

Sur GitHub/GitLab, configurez au minimum :
- **Branch protection** sur `main` : interdire les push directs, exiger une PR pour fusionner
- **Require pull request before merging** : garantir que chaque changement est relu

Ces protections ne prennent que quelques minutes et évitent des erreurs irréversibles.

### Conseil 7 — Documenter les problèmes rencontrés

Tenez un petit fichier `NOTES.md` dans le dépôt (ou dans votre environnement personnel) où chaque erreur rencontrée et sa solution sont notées. Ce document deviendra une ressource précieuse pour les jours suivants et pour le Debug CSV, le Troubleshooting et la préparation du Demo Day.

### Conseil 8 — Vérifier la présence de secrets avant chaque push

Prenez l'habitude de lancer cette commande avant chaque `git push` :
```bash
git grep -nE "(api[_-]?key|password|secret|token)" -- . ":(exclude).env.example"
```
Si des résultats apparaissent hors de `.env.example`, corrigez immédiatement.

---

## 9. Résumé visuel de la matinée

```
09h00 ┌──────────────────────────────────────────────────┐
      │  Accueil & QCM de positionnement                  │
      │  → Cartographier les niveaux du groupe            │
09h30 ├──────────────────────────────────────────────────┤
      │  Constitution des binômes & peer-programming     │
      │  → Pilote (avancé) guide, Copilote (débutant)    │
      │    tape                                         │
10h00 ├──────────────────────────────────────────────────┤
      │  Installation environnement                     │
      │  VS Code · Git · Python 3.10+ · Docker · SSH    │
      │  PATH · WSL2                                    │
11h15 ├──────────────────────────────────────────────────┤
      │  Git & Jalon 1                                  │
      │  Clone · Status · Add · Commit · Branch · PR    │
      │  → Dépôt officiel + README + première PR        │
12h00 └──────────────────────────────────────────────────┘
```

---

## 10. Commandes essentielles à conserver

### Gestion du dépôt

```bash
git clone https://github.com/groupe/depot.git
cd depot
git status
git switch -c docs/readme
git add README.md .gitignore .env.example
git commit -m "docs: initialise le projet"
git push -u origin docs/readme
git checkout main
git merge docs/readme
git push origin main
```

### Vérification de l'environnement

```bash
python --version       # attendu : Python 3.10+
git --version          # attendu : 2.30+
docker --version       # attendu : Docker 20.10+
docker compose version # attendu : Docker Compose v2
git config --list      # vérifie user.name et user.email
ssh -T git@github.com  # test de la clé SSH
```

### Sécurité du dépôt

```bash
git grep -nE "(api[_-]?key|password|secret)" -- . ":(exclude).env.example"
git check-ignore -v .env
cat .gitignore
```

---

> **Mot de fin pour l'orateur** : Cette matinée a posé deux choses impossibles à rattraper demain : un environnement qui fonctionne et un dépôt partagé. Chaque minute investie aujourd'hui dans la configuration, les conventions Git et la qualité du README sera remboursée dix fois demain, lorsque le code sera écrit, testé et démontré. Que chaque binôme parte avec un `git status` propre et un dépôt cloné sur les deux machines — c'est le critère de réussite de ce jour.
