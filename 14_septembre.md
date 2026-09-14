# Jour 6 - Lundi 14 septembre

## Des logs bruts à une alerte exploitable

### Semaine 2 · Data, IA et livrables du projet

---

> **À propos de ce document** : Ce fichier est un guide d'explication orale complet pour le Jour 6. Il est conçu pour être lu à voix haute devant le groupe. Chaque section est structurée pour faciliter la compréhension, avec des exemples concrets, des encadrés de conseil et des mises en garde.

---

## 1. Résumé exécutif du jour

Le Jour 6 marque une transition cruciale dans le projet : nous passons de la manipulation de données en mémoire (listes Python, fichiers JSON/CSV) à la **persistance durable** dans PostgreSQL. Jusqu'à aujourd'hui, les logs ingérés par l'API pouvaient disparaître dès l'arrêt de l'application. Désormais, ils survivent au redémarrage, aux conteneurs, et même à l'arrêt de la machine.

Ce jour est le **pont entre l'ingestion (semaine 1) et l'analyse IA (demain)**. Sans base de données persistante, l'analyse IA n'aurait sur quoi travailler : les logs seraient éphémères, les analyses impossibles à retracer, et l'historique des événements perdu. La modélisation SQL que nous étudions aujourd'hui est la colonne vertébrale de tout le projet.

**Le fil rouge du projet** : un événement technique (log) entre dans l'API, est validé, est **persisté dans PostgreSQL**, puis demain sera analysé par une IA pour produire une alerte exploitabile. Aujourd'hui, nous construisons l'étape « persisté » de ce parcours.

---

## 2. Objectifs pédagogiques du jour

À l'issue de cette session, chaque binôme sera capable de :

- **Différencier SQL et NoSQL** et choisir le bon outil selon le besoin
- **Modéliser des tables** avec des clés primaires et étrangères pour les logs et analyses
- **Rédiger des requêtes SQL** basiques : SELECT, INSERT, UPDATE, JOIN
- **Interroger une instance PostgreSQL** exécutée sous Docker
- **Connecter l'API FastAPI** au conteneur PostgreSQL via une variable DATABASE_URL
- **Créer un volume Docker persistant** pour conserver les données au-delà du cycle de vie du conteneur
- **Implémenter des filtres** sur l'endpoint GET /logs

### Objectifs mesurables

| Objectif | Critère de réussite |
|----------|---------------------|
| Modélisation SQL | Les tables logs et analyses sont conçues avec les bonnes clés et relations |
| Connexion DB | L'API se connecte à PostgreSQL sans erreur, confirmé par GET /health |
| Persistance | Un log inséré avant un redémarrage est retrouvé après |
| Filtres | GET /logs?level=ERROR&source=api retourne uniquement les logs correspondants |
| Volume Docker | Les données survivent à un docker compose down suivi de docker compose up |

---

## 3. Détaillage horaire
### 3.1 · 09h00-09h40 — Modélisation & base SQL

#### Comparer SQL et NoSQL

Avant de taper une seule ligne de code, il faut comprendre **quel type de base de données** convient à notre projet.

**SQL (Relationnel)** :
- Les données sont organisées en **tables** avec des colonnes de types définis
- Les relations entre tables sont exprimées par des **cles étrangères**
- Langage standardisé : SQL (Structured Query Language)
- Exemples : PostgreSQL, MySQL, SQLite
- Idéal pour des données structurées avec des relations claires (logs -> analyses)

**NoSQL (Non-relational)** :
- Différents modèles : documents (MongoDB), clé-valeur (Redis), graphe (Neo4J), wide-column (Cassandra)
- Pas de schéma rigide pré-défini
- Plus flexible pour des données hétérogènes ou en évolution rapide
- Moins bien adapté pour des relations complexes entre entités

> **Encadré — Pourquoi SQL pour notre projet ?**
> Nos logs et analyses ont une structure claire et stable : un log a un ID, un niveau, un message, une source, un horodatage. Une analyse est liée à un log par son ID. Ces relations sont **bien définies, stables et structurées**. SQL est l'outil idéal. Un NoSQL comme MongoDB pourrait fonctionner, mais nous perdrions la puissance des requêtes relationnelles (JOIN, filtres complexes) et la garantie de cohérence des types.

#### Étudier les tables, clés primaires et étrangères

La modélisation est le premier geste de tout bon développeur base de données. Elle se fait sur papier (ou dans sa tête) avant de taper une seule commande.

**La table `logs`** :
- Chaque ligne représente un événement technique reçu par l'API
- Colonnes : id, occurred_at, level, message, source, metadata, created_at
- La **clé primaire** est `id` : elle identifie chaque ligne de manière unique et auto-incrémentée

**La table `analyses`** :
- Chaque ligne représente le résultat d'une analyse IA sur un log
- Colonnes : id, log_id, severity, category, summary, recommendations, provider, created_at
- La **clé primaire** est `id`
- La **clé étrangère** est `log_id` : elle fait référence à `logs.id` et crée le lien entre une analyse et son log source

> **Encadré — Clé primaire vs Clé étrangère**
> - **Clé primaire** : l'identifiant unique d'une ligne dans sa propre table. Comme un numéro de dossier. Une table n'en a qu'une.
> - **Clé étrangère** : une colonne qui pointe vers la clé primaire d'une autre table. Elle établit une relation entre deux tables. Une table peut avoir plusieurs clés étrangères.
>
> Dans notre cas : `analyses.log_id` -> `logs.id`. Si on supprime un log, la clause `ON DELETE CASCADE` supprime automatiquement les analyses qui y sont liées.

#### Les quatre commandes SQL fondamentales

**SELECT — Lire des données**
sql
SELECT id, level, message FROM logs WHERE level = 'ERROR' ORDER BY occurred_at DESC LIMIT 10;

**INSERT — Ajouter une ligne**
sql
INSERT INTO logs (level, message, source) VALUES ('ERROR', 'Connection timeout', 'api');

**UPDATE — Modifier des lignes**
sql
UPDATE logs SET source = 'api-gateway' WHERE id = 42;

**JOIN — Combiner deux tables**
sql
SELECT logs.id, logs.message, analyses.severity
FROM logs
JOIN analyses ON analyses.log_id = logs.id
WHERE analyses.severity = 'CRITICAL';

> **Encadré — Le piège de la concatenation SQL**
> Ne construites jamais une requête en collant directement une valeur utilisateur :
> sql
> -- À NE JAMAIS FAIRE
> query = f"SELECT * FROM logs WHERE message = '{user_input}'"
> 
> -- TOUJOURS UTILISER DES PARAMÈTRES
> query = "SELECT * FROM logs WHERE message = :msg"
> cursor.execute(query, {"msg": user_input})
>
> Cela prévient les **injections SQL**, une vulnérabilité critique vue au Jour 4. FastAPI et SQLAlchemy utilisent déjà ce mécanisme de paramétrisation.

---
### 3.2 · 09h40-10h30 — Requêtage SQL

Cette tranche est pratique : nous allons **interroger une instance PostgreSQL** exécutée sous Docker. L'objectif est de prendre en main le langage SQL dans un environnement proche de celui utilisé en production.

#### Démarrer le conteneur PostgreSQL

Avec Docker Compose, une seule commande suffit :
bash
docker compose up -d db

Le service `db` utilise l'image `postgres:15-alpine` et expose les données via un **volume nommé** `postgres_data`. Ce volume est la garantie que les données survivent au conteneur.

#### Se connecter au conteneur

Pour exécuter des requêtes SQL directement, on utilise `docker compose exec` :
bash
docker compose exec db psql -U bootcamp -d music_hall

Une fois connecté, on peut tester les quatre commandes fondamentales :

**Lire les logs**
sql
SELECT id, level, message, source, occurred_at 
FROM logs 
ORDER BY occurred_at DESC 
LIMIT 5;

**Insérer un log de test**
sql
INSERT INTO logs (level, message, source) 
VALUES ('ERROR', 'Connection refused to database', 'api-gateway');

**Modifier un log**
sql
UPDATE logs SET source = 'auth-service' WHERE id = 1;

**Joindre logs et analyses**
sql
SELECT l.id, l.message, a.severity, a.category
FROM logs l
JOIN analyses a ON a.log_id = l.id
WHERE a.severity = 'HIGH';

> **Encadré — SQLite vs PostgreSQL**
> Pour les tests rapides, **SQLite** est une base en fichier local, sans serveur, ultra-rapide à installer. Parfaite pour les exercices unitaires ou le développement initial.
> 
> **PostgreSQL** est un serveur complet, mult-utilisateur, avec des fonctionnalités avancées (contraintes, index, roles, replication). C'est la base utilisée en production.
>
> En Docker, la différence est invisible : on utilise la même syntaxe SQL. La seule différence technique est la façon de s'y connecter (socket local pour SQLite, TCP pour PostgreSQL).

#### Les filtres WHERE

La clause WHERE permet de restreindre les résultats :
sql
-- Par niveau
SELECT * FROM logs WHERE level = 'ERROR';

-- Par source
SELECT * FROM logs WHERE source = 'api-gateway';

-- Par période
SELECT * FROM logs WHERE occurred_at > NOW() - INTERVAL '1 hour';

- **`=`** : égalité
- **`>` / `<`** : comparaison
- **`LIKE`** : recherche de motif (`WHERE message LIKE '%timeout%'`)
- **`IN`** : liste de valeurs (`WHERE level IN ('ERROR', 'CRITICAL')`)
- **`AND` / `OR`** : combiner plusieurs conditions

---
### 3.3 · 10h30-11h30 — Fil rouge · Jalon 6 : Connecter l'API au conteneur PostgreSQL

C'est le moment de la mise en pratique : **connecter l'API FastAPI au conteneur PostgreSQL** et stocker les logs de façon structurée.

#### La variable DATABASE_URL

La connexion à la base se fait par une **variable d'environnement** `DATABASE_URL`. Elle contient l'URL complète avec l'utilisateur, le mot de passe, l'hôte et le nom de la base :
bash
# Format
postgresql://utilisateur:motdepasse@nom-du-conteneur:5432/nom-de-la-base

# Exemple concret
postgresql://bootcamp:secret@db:5432/music_hall

> **Encadré — Pourquoi une variable d'environnement ?**
> - **Sécurité** : le mot de passe n'est pas dans le code source
> - **Flexibilité** : la même application tourne en local (SQLite), en dev (PostgreSQL local), en prod (PostgreSQL distant)
> - **Convention** : c'est le standard des applications modernes. L'intervenant a déjà mis en place ce mécanisme au Jour 5.

Dans l'application, la variable est lue par `python-dotenv` (le `.env` local) ou par le système de secrets Docker (en production).

#### Le volume persistant

Sans volume, les données de PostgreSQL vivent **uniquement dans le conteneur**. Si on détruit le conteneur (par exemple avec `docker compose down` puis `docker compose up`), toutes les tables et données disparaissent.

La solution : un **volume nommé** dans `compose.yaml` :
yaml
volumes:
  postgres_data:

services:
  db:
    volumes:
      - postgres_data:/var/lib/postgresql/data

Avec cette configuration :
- `docker compose up` : PostgreSQL crée les tables (grâce à `init-db.sql`)
- `docker compose down` : le conteneur s'arrête, mais les données restent sur le volume
- `docker compose up` : PostgreSQL redémarre et retrouve les mêmes données

> **Encadré — Le test de persistance**
> 1. Insérer un log via l'API ou directement en SQL
> 2. Arrêter les services : `docker compose down`
> 3. Relancer : `docker compose up -d`
> 4. Vérifier que le log est toujours là : `curl /logs`
>
> Si le log a disparu, le volume n'est pas configuré correctement. C'est le test numéro 1 à faire.

#### Le schéma de la base

Le script `init-db.sql` (déjà présent dans le dépôt) crée les tables au premier démarrage :
sql
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    source VARCHAR(100),
    metadata TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS analyses (
    id SERIAL PRIMARY KEY,
    log_id INTEGER NOT NULL REFERENCES logs(id) ON DELETE CASCADE,
    severity VARCHAR(20) NOT NULL,
    category VARCHAR(100) NOT NULL,
    summary TEXT NOT NULL,
    recommendations TEXT NOT NULL,
    provider VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

L'application utilise également SQLAlchemy (dans `app.py`) pour créer les tables automatiquement avec `Base.metadata.create_all()`. Les deux mécanismes sont complémentaires et ne se conflitent pas.

#### Les filtres GET /logs

L'endpoint `GET /logs` permet de **lister et filtrer** les logs stockés :
bash
# Tous les logs (limite 100 par défaut)
curl "http://localhost:5000/logs"

# Uniquement les erreurs
curl "http://localhost:5000/logs?level=ERROR"

# Par source
curl "http://localhost:5000/logs?source=api-gateway"

# Combinaison des deux
curl "http://localhost:5000/logs?level=ERROR&source=api-gateway&limit=50"

Dans le code, ces filtres se traduisent par des clauses WHERE dynamiques :
python
stmt = select(Log)
if level:
    stmt = stmt.where(Log.level == level)
if source:
    stmt = stmt.where(Log.source == source)
stmt = stmt.order_by(Log.created_at.desc()).limit(limit)

> **Encadré — Sécurité des filtres**
> Les valeurs de `level` et `source` proviennent de l'utilisateur (paramètres URL). Elles sont **validées** avant utilisation : le niveau doit faire partie de la liste autorisée, la source ne peut pas être vide. Et elles sont passées par **paramètres** (SQLAlchemy), jamais par concatenation de chaînes.

---
### 3.4 · 11h30-12h00 — Débrief & Q&A : Diagnostiquer la communication inter-conteneurs et Docker network

Cette dernière tranche est consacrée au **débogage** des problèmes les plus fréquents lors de la communication entre conteneurs.

#### Le réseau Docker

Quand on lance `docker compose up`, Docker crée un **réseau par défaut** (généralement nommé `nom-du-projet_default`). Tous les services définis dans `compose.yaml` y sont connectés. Dans ce réseau, chaque service est accessible par **son nom** :

- Le service `web` (FastAPI) peut appeler le service `db` (PostgreSQL) à l'adresse **`db`**
- Le service `db` est accessible depuis `web` via **`db:5432`**
- Mais `localhost` depuis `web` ne désigne pas la machine hôte, il désigne le conteneur `web` lui-même

> **Encadré — Le piège de localhost**
> Depuis le terminal de votre ordinateur, `localhost:5000` c'est l'API FastAPI.
> Depuis le conteneur `web`, `localhost:5000` c'est... le conteneur `web` lui-même.
> Depuis le conteneur `web`, pour parler à PostgreSQL, il faut utiliser `db:5432`, pas `localhost:5432`.
>
> C'est la confusion la plus courante au début de l'utilisation de Docker.

#### Les symptômes et leurs cause

| Symptôme | Cause probable | Solution |
|----------|---------------|----------|
| `Connection refused` au démarrage | La base n'est pas encore prête | `depends_on` avec `condition: service_healthy` |
| `could not connect to server` | L'adresse est mauvaise | Vérifier `DB_HOST=db` dans `.env` |
| `password authentication failed` | Le mot de passe est incorrect | Vérifier les secrets Docker ou `.env` |
| Les données disparaissent | Aucun volume configuré | Ajouter `postgres_data:/var/lib/postgresql/data` |
| Le conteneur redémarre en boucle | La base n'est pas accessible | Vérifier le réseau et la variable `DATABASE_URL` |

#### Les outils de diagnostic

**Voir l'état des conteneurs**
bash
docker compose ps

**Suivre les logs**
bash
docker compose logs -f db    # Logs de PostgreSQL
docker compose logs -f web   # Logs de l'API

**Exécuter une commande dans un conteneur**
bash
docker compose exec db psql -U bootcamp -d music_hall
docker compose exec web env  # Voir les variables d'environnement

**Vérifier le réseau**
bash
docker network ls
docker inspect <nom-du-reseau>

**Voir les variables dans le conteneur**
bash
docker compose exec web env | grep DATABASE

---
## 4. Concepts clés expliqués simplement

### 4.1 · SQL vs NoSQL

| Critère | SQL (PostgreSQL) | NoSQL (MongoDB, Redis) |
|---------|------------------|------------------------|
| **Modèle** | Table-lignes-colonnes | Documents, clé-valeur, graphe |
| **Schéma** | Rigide, défini à l'avance | Flexible, évolutive |
| **Relations** | Clés étrangères, JOIN | Imbuées ou à gérer côté applicatif |
| **Requêtes** | SQL standardisé | API spécifique par moteur |
| **Échelle** | Vertical (plus de puissance) | Horizontal (plus de serveurs) |
| **Notre cas** | **Idéal** : logs et analyses structurées | Inutile : pas de besoin de flexibilité |

**Règle pratique** : si tu as des entités avec des relations claires (« une analyse appartient à un log »), privilégie SQL. Si tu as des données hétérogènes, en constante évolution, ou sans relations nettes, envisage NoSQL.

### 4.2 · Table, Ligne, Colonne

- **Table** : une collection de données structurées. Comme une feuille de calcul avec des colonnes nommées.
- **Ligne** (ou enregistrement) : une instance concrète d'une entité. Une ligne dans `logs` = un événement.
- **Colonne** : un attribut d'une entité. `level`, `message`, `source` sont des colonnes de la table `logs`.

### 4.3 · Clé primaire et Clé étrangère

**Clé primaire (Primary Key)** :
- Identifie **uniquement** chaque ligne d'une table
- Ne peut pas être nulle, pas duplicates
- Souvent un `id` auto-incrémenté
- Analogie : le numéro de série d'un produit

**Clé étrangère (Foreign Key)** :
- Une colonne d'une table qui **fait référence** à la clé primaire d'une autre table
- Elle établit une **relation** entre deux tables
- Dans `analyses`, `log_id` est une clé étrangère pointant vers `logs.id`

**Les relations** :
- **Un-à-un (1:1)** : une ligne d'une table est liée à une seule ligne d'une autre
- **Un-à-plusieurs (1:N)** : une ligne de `logs` peut avoir plusieurs `analyses` (notre cas)
- **Plusieurs-à-plusieurs (M:N)** : nécessite une table intermédiaire

### 4.4 · Les requêtes SQL

**SELECT** : lire
sql
SELECT colonnes FROM table WHERE condition;

**INSERT** : ajouter
sql
INSERT INTO table (colonnes) VALUES (valeurs);

**UPDATE** : modifier
sql
UPDATE table SET colonne = valeur WHERE condition;

**DELETE** : supprimer
sql
DELETE FROM table WHERE condition;

**JOIN** : combiner
sql
SELECT * FROM table_a JOIN table_b ON table_a.cle = table_b.cle;

> **Attention** : `UPDATE` et `DELETE` sans clause `WHERE` modifient/suppriment **toutes** les lignes. Toujours vérifier avec un `SELECT` avant.

### 4.5 · Volume Docker

Un **volume** est un espace de stockage persistant géré par Docker, situé sur la machine hôte. Il survive au conteneur qui l'utilise.

**Sans volume** :
- Les données vivent dans le conteneur
- `docker compose down` + `docker compose up` = base vide

**Avec volume** :
- Les données sont stockées sur le disque hôte
- `docker compose down` + `docker compose up` = données intactes

**Commandes utiles** :
bash
docker volume ls              # Lister les volumes
docker volume inspect <nom>   # Voir les détails
docker volume prune           # Supprimer les volumes non utilisés

---
## 5. Livrables attendus — Jalon 6

| Livrable | Description | Critère de qualité |
|----------|-------------|-------------------|
| **Tables logs et analyses** | Créées dans PostgreSQL via `init-db.sql` ou SQLAlchemy | Bonnes clés primaires/étrangères, index sur les colonnes filtrées |
| **Connexion DATABASE_URL** | Variable d'environnement configurée dans `.env` et `compose.yaml` | L'API démarre sans erreur, `GET /health` retourne `database: up` |
| **Volume persistant** | `postgres_data` déclaré dans `compose.yaml` | Les données survivent à un `docker compose down` + `docker compose up` |
| **Filtres GET /logs** | Filtrage par `level`, `source` et `limit` | Chaque fil fonctionne seul et combiné avec les autres |
| **Validation des filtres** | Les valeurs invalides sont rejetées avec un message clair | `level=BOGUS` retourne 400, pas un résultat vide |

### Definition of Done du Jalon 6

- [ ] Les tables `logs` et `analyses` existent dans PostgreSQL
- [ ] Un log inséré par l'API est visible via `GET /logs`
- [ ] Les données survivent au redémarrage des conteneurs
- [ ] Les filtres `level` et `source` fonctionnent
- [ ] Les requêtes utilisent des paramètres (SQLAlchemy), jamais de concatenation SQL
- [ ] Le volume `postgres_data` est présent dans `docker volume ls`

---

## 6. Erreurs fréquentes et comment les éviter

### Erreur 1 — Oublier le volume et perdre les données

**Le problème** : Les logs disparaissent après un `docker compose down` + `docker compose up`. Le conteneur est recréé avec un filesystem propre.

**La solution** : Ajouter un volume nommé dans `compose.yaml` :
yaml
volumes:
  postgres_data:

services:
  db:
    volumes:
      - postgres_data:/var/lib/postgresql/data

**Test de validation** : Insérer un log, arrêter les services, relancer, vérifier que le log est toujours là.

### Erreur 2 — Construire une requête SQL en collant une valeur utilisateur

**Le problème** :
python
# À NE JAMAIS FAIRE
query = f"SELECT * FROM logs WHERE message = '{user_input}'"
cursor.execute(query)

C'est une **injection SQL** : un utilisateur peut modifier la requête et accéder, modifier ou supprimer des données.

**La solution** : Toujours utiliser des paramètres :
python
# ✅
query = "SELECT * FROM logs WHERE message = :msg"
cursor.execute(query, {"msg": user_input})

FastAPI et SQLAlchemy utilisent déjà ce mécanisme de paramétrisation.

### Erreur 3 — Confondre `localhost` et le nom du service Docker

**Le problème** : Depuis le conteneur `web`, utiliser `localhost:5432` pour parler à PostgreSQL. `localhost` depuis un conteneur désigne le conteneur lui-même, pas la machine hôte.

**La solution** : Dans `compose.yaml`, les services communiquent par leur **nom** (`db`, `web`), pas par `localhost`. La variable `DATABASE_URL` doit contenir `db` comme hôte.

### Erreur 4 — Ne pas valider les entrées avant de les stocker

**Le problème** : Insérer un log avec un niveau inexistant (`level = 'BOGUS'`) ou un message vide. La base contient des données invalides.

**La solution** : Valider avant de stocker. FastAPI et Pydantic le font déjà dans le code actuel. Les niveaux validés sont : `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

### Erreur 5 — Créer trop de tables ou trop de champs

**Le problème** : Modéliser des centaines de tables et de colonnes avant d'avoir testé le chemin minimal. Complexité inutile, maintenance difficile.

**La solution** : Commencer avec le minimum :
- `logs` : id, occurred_at, level, message, source, metadata, created_at
- `analyses` : id, log_id, severity, category, summary, recommendations, provider, created_at

Ajouter des colonnes ou tables seulement si le besoin est réel.

### Erreur 6 — Ne pas attendre que la base soit prête

**Le problème** : L'API démarre avant PostgreSQL. La première requête échoue avec `Connection refused`.

**La solution** : Utiliser `depends_on` avec une condition de santé :
yaml
depends_on:
  db:
    condition: service_healthy

L'application a également une logique de reconnexion (`wait_for_db`) qui réessaie plusieurs fois.

### Erreur 7 — Modifier `UPDATE` ou `DELETE` sans clause WHERE

**Le problème** :
sql
UPDATE logs SET level = 'INFO';  -- Tous les logs deviennent INFO
sql
DELETE FROM logs;  -- Tous les logs sont supprimés

**La solution** : Toujours vérifier avec un `SELECT` avant d'exécuter un `UPDATE` ou `DELETE` massif. Pour les suppressions, utiliser `TRUNCATE` uniquement si on veut vider complètement une table.

---
## 7. Connexions avec les jours suivants

Le Jour 6 n'est pas une fin en soi : chaque concept étudie aujourd'hui est **utilisé et approfondi** dans les jours à venir.

### Jour 7 (Mardi 15 septembre) — Intégration de l'IA & APIs REST

- **Les logs stockés** en PostgreSQL aujourd'hui sont les **données d'entrée** de l'analyse IA de demain
- L'endpoint `POST /logs/{id}/analyze` a besoin d'un `log_id` qui existe dans la base — c'est pour cela qu'on persiste les logs
- La table `analyses` créée aujourd'hui sera **remplie demain** par le résultat de l'IA

### Jour 8 (Mercredi 16 septembre) — Sprint de développement

- Toute la logique de stockage et de requêtage est **stabilisée** : le sprint peut commencer
- Les filtres GET /logs sont étendus et affinés pour la démonstration

### Jour 9 (Jeudi 17 septembre) — Testing, documentation & finalisation

- Les tests unitaires vérifient que la connexion à la base fonctionne
- Le volume persistant est testé pour s'assurer que les données survivent au redémarrage

### Jour 10 (Vendredi 18 septembre) — Restitution, Demo Day & closing

- La démonstration montre l'**ensemble du flux** : log entre → persisté → analysé → alerte
- Les logs stockés aujourd'hui servent de **jeu de données** pour la démo

> **Encadré — Le domino du Jour 6**
> Si la base de données n'est pas persistante, l'analyse IA de demain n'a rien à analyser. Si les filtres ne fonctionnent pas, la démo de vendredi est incomplète. La persistance est la base sur laquelle tout le reste s'élève.

---

## 8. Pour aller plus loin — Conseils pratiques

### Conseil 1 — Apprendre SQL par les exemples

La meilleure façon d'apprendre SQL est d'**exécuter** des requêtes sur des données réelles. Commencer par :
sql
-- Voir la structure des tables
\d logs
\d analyses

-- Compter les logs par niveau
SELECT level, COUNT(*) FROM logs GROUP BY level;

-- Trouver les logs les plus récents
SELECT * FROM logs ORDER BY occurred_at DESC LIMIT 3;

### Conseil 2 — Maîtriser le volume Docker

Le volume est invisible mais crucial. Pour le vérifier :
bash
docker volume ls
docker volume inspect postgres_data

Si les données disparaissent, vérifiez que le volume est bien déclaré dans `compose.yaml` et que le chemin de montage est correct (`/var/lib/postgresql/data`).

### Conseil 3 — Toujours valider avant de stocker

La validation est le **filet de sécurité** entre l'utilisateur et la base de données. Elle empêche :
- Les données invalides (un niveau inexistant)
- Les données trop longues (un message de 10 000 caractères)
- Les attaques (injection SQL)

FastAPI et Pydantic font déjà ce travail. Vérifiez que chaque champ a les bonnes contraintes (type, longueur, valeurs autorisées).

### Conseil 4 — Utiliser les index pour les performances

Au fur et à mesure que la base grossit, certaines requêtes ralentissent. Les **index** accélèrent les recherches :
sql
CREATE INDEX idx_logs_level ON logs(level);
CREATE INDEX idx_logs_source ON logs(source);
CREATE INDEX idx_analyses_log_id ON analyses(log_id);
CREATE INDEX idx_analyses_severity ON analyses(severity);

Ces index sont déjà présents dans `init-db.sql`.

### Conseil 5 — Tester la persistance dès le début

Dès que la base fonctionne, faire le test :
1. Insérer un log
2. `docker compose down`
3. `docker compose up -d`
4. Vérifier que le log est toujours là

Si le test échoue, le problème est facile à identifier. S'il est reporté à la fin du projet, il devient difficile à diagnostiquer.

### Conseil 6 — Documenter le schéma de la base

Garder une copie du schéma (le `init-db.sql` ou un diagramme) à jour. C'est la **référence** pour :
- Comprendre comment les données sont organisées
- Ajouter de nouvelles tables ou colonnes
- Déboguer des problèmes de requêtes

### Conseil 7 — Pratiquer les JOIN

Les JOIN sont l'une des opérations les plus utiles en SQL. Pratiquer avec des exemples concrets :
sql
-- Logs sans analyse
SELECT l.id, l.message FROM logs l
LEFT JOIN analyses a ON a.log_id = l.id
WHERE a.id IS NULL;

-- Logs avec leur analyse
SELECT l.message, a.severity, a.category
FROM logs l
INNER JOIN analyses a ON a.log_id = l.id;

### Conseil 8 — Sécuriser les connexions base de données

- **Jamais** de mot de passe en clair dans le code
- Utiliser `.env` en local, des **secrets Docker** en production
- Changer les mots de passe régulièrement
- Ne pas utiliser le compte `root` pour l'application : créer un compte dédié (`bootcamp`)

---
## 9. Résumé visuel de la matinée

```
09h00 ┌──────────────────────────────────────────────────┐
      │  Modélisation & base SQL                          │
      │  → SQL vs NoSQL, tables, clés, SELECT/INSERT/JOIN│
09h40 ├──────────────────────────────────────────────────┤
      │  Requêtage SQL                                    │
      │  → Interroger PostgreSQL sous Docker              │
10h30 ├──────────────────────────────────────────────────┤
      │  Fil rouge · Jalon 6                              │
      │  → Connecter l'API à PostgreSQL                   │
      │  → Volume persistant, filtres GET /logs           │
11h30 ├──────────────────────────────────────────────────┤
      │  Débrief & Q&A                                    │
      │  → Communication inter-conteneurs, débogage       │
12h00 └──────────────────────────────────────────────────┘
```

---

## 10. Commandes essentielles à conserver

### Gestion des conteneurs
bash
docker compose up -d              # Démarrer les services
docker compose down               # Arrêter les services
docker compose restart            # Redémarrer
docker compose ps                 # Voir l'état des services
docker compose logs -f db         # Suivre les logs de PostgreSQL

### Requêter la base
bash
# Depuis le conteneur
docker compose exec db psql -U bootcamp -d music_hall

# Depuis l'API
curl "http://localhost:5000/logs"
curl "http://localhost:5000/logs?level=ERROR&limit=10"
curl "http://localhost:5000/logs/{id}"

# Vérifier la santé
curl http://localhost:5000/health

### Volumes
bash
docker volume ls
docker volume inspect postgres_data

### Vérifier la persistance
bash
# 1. Insérer un log
curl -X POST http://localhost:5000/logs -H "Content-Type: application/json" \
  -d '{"message":"Test persistence","level":"INFO","source":"test"}'

# 2. Arrêter et relancer
docker compose down
docker compose up -d

# 3. Vérifier que le log est toujours là
curl "http://localhost:5000/logs"

### Schéma de la base
sql
-- Voir les tables
\dt

-- Voir la structure d'une table
\d logs
\d analyses

-- Compter les logs
SELECT level, COUNT(*) FROM logs GROUP BY level;

### Requêtes utiles
sql
-- Logs récents avec leur analyse
SELECT l.id, l.message, l.level, a.severity, a.category
FROM logs l
LEFT JOIN analyses a ON a.log_id = l.id
ORDER BY l.occurred_at DESC
LIMIT 20;

-- Logs sans analyse
SELECT l.id, l.message FROM logs l
LEFT JOIN analyses a ON a.log_id = l.id
WHERE a.id IS NULL;

-- Statistiques par niveau
SELECT level, COUNT(*) as nb, MIN(occurred_at) as premier, MAX(occurred_at) as dernier
FROM logs
GROUP BY level
ORDER BY nb DESC;

---

## 11. Checklist de fin de journée

- [ ] Les tables `logs` et `analyses` existent dans PostgreSQL
- [ ] Un log inséré par l'API est visible via `GET /logs`
- [ ] Les filtres `level` et `source` fonctionnent
- [ ] Les données survivent au redémarrage des conteneurs
- [ ] `GET /health` retourne `{"status":"ok","database":"up"}`
- [ ] Le volume `postgres_data` est présent dans `docker volume ls`
- [ ] Les requêtes utilisent des paramètres (SQLAlchemy), jamais de concatenation SQL
- [ ] La variable `DATABASE_URL` est configurée dans `.env` (pas dans le code)

---

> **Mot de fin pour l'orateur** : Aujourd'hui, vous avez posé la **colonne vertébrale** du projet. Sans persistance, pas d'historique, pas d'analyse IA, pas d'alertes exploitables. Chaque minute passée sur la modélisation SQL, le volume Docker et les filtres GET /logs est un investissement direct dans la démonstration de vendredi. Le test de persistance (insérer, arrêter, relancer, vérifier) est le plus important : il prouve que la base de données est vraiment durable.
