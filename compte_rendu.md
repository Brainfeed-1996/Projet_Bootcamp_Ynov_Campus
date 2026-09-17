# Compte rendu — Bootcamp DevSecOps

## Période couverte

Ce compte rendu synthétise les documents quotidiens du **7 septembre au 18 septembre** pour le projet **« Des logs bruts à une alerte exploitable »**.

- **Semaine 1 — Socle systèmes, infrastructure et sécurité :** du lundi 7 au vendredi 11 septembre.
- **Week-end des 12 et 13 septembre :** aucun fichier quotidien n'est présent dans le dossier.
- **Semaine 2 — Data, IA, intégration et restitution :** du lundi 14 au vendredi 18 septembre.

L'objectif final est de livrer une API FastAPI conteneurisée capable d'ingérer des logs JSON ou CSV, de les valider, de les persister dans PostgreSQL, de les analyser avec un fournisseur IA remplaçable, puis de produire une alerte exploitable. Le tout doit être documenté, testé, sécurisé et démontrable en six minutes.

## 1. Vue d'ensemble de la progression

| Date | Jour | Thème principal | Jalon ou résultat |
|---|---:|---|---|
| 7 septembre | 1 | Environnement, Git et collaboration | Jalon 1 : dépôt fonctionnel, README et première PR |
| 8 septembre | 2 | Linux, Bash et réseau | Jalon 2 : architecture réseau et scripts d'initialisation/lancement |
| 9 septembre | 3 | Docker et parsing Python | Jalon 3 : endpoint `POST /logs` conteneurisé |
| 10 septembre | 4 | Cyber offensive et OWASP | Jalon 4 : audit, preuves reproductibles et tickets de remédiation |
| 11 septembre | 5 | Cyber défensive et DevSecOps | Jalon 5 : validation stricte, secrets et durcissement Docker |
| 14 septembre | 6 | PostgreSQL et persistance | Jalon 6 : stockage durable et filtres API |
| 15 septembre | 7 | Intelligence artificielle et API REST | Jalon 7 : analyse structurée et fournisseur IA interchangeable |
| 16 septembre | 8 | Sprint d'intégration globale | Assemblage API + PostgreSQL + IA et préparation du code freeze |
| 17 septembre | 9 | Tests, documentation et finalisation | Jalon 8 : code freeze, qualité, packaging et répétition |
| 18 septembre | 10 | Demo Day et clôture | Démonstration, questions-réponses, feedback et bilan |

---

# Partie 1 — Semaine 1 : socle systèmes, infrastructure et sécurité

## 2. Lundi 7 septembre — Jour 1 : environnement, Git et première collaboration

### Objectif du jour

Mettre en place un environnement de développement exploitable et créer les bases de collaboration du binôme. Le jour commence avec un accueil, un QCM de positionnement et la formation de binômes associant un profil avancé à un profil débutant.

### Travail réalisé

- Installation et vérification de **VS Code**, Git, Python 3.10 ou plus, Docker Desktop, WSL2 selon les besoins et les clés SSH.
- Configuration de Git avec un nom d'utilisateur et une adresse email.
- Vérification des commandes `python --version`, `git --version`, `docker --version` et `docker compose version`.
- Mise en place du workflow Git : clone, `git status`, branche, ajout, commit, push et Pull Request.
- Création d'une branche documentaire, rédaction du premier `README.md`, ajout de `.gitignore` et `.env.example`, puis fusion par Pull Request.
- Adoption du peer-programming : le profil débutant garde le clavier, le profil avancé guide et explique.
- Définition de l'architecture cible : client ou curl vers FastAPI, PostgreSQL pour la persistance, fournisseur IA pour l'analyse, Swagger UI pour la démonstration.

### Notions importantes

- Un commit doit représenter une intention unique et porter un message clair.
- Une branche isole une modification avant sa revue et sa fusion.
- Une Pull Request permet la relecture avant intégration dans `main`.
- `.gitignore` protège les secrets, les environnements virtuels, les caches et les données locales.
- `localhost` n'a pas la même signification sur l'hôte et dans un conteneur Docker.

### Livrables du Jalon 1

- Dépôt distant accessible et cloné sur les deux machines.
- README décrivant le projet, la stack et le démarrage.
- `.gitignore` et `.env.example` sans valeur réelle.
- Branche de travail et première PR relue et fusionnée.
- Historique Git sans secret.

## 3. Mardi 8 septembre — Jour 2 : Linux, scripting Bash et réseau

### Objectif du jour

Acquérir les bases de la ligne de commande Linux, comprendre les flux réseau et automatiser le démarrage du projet avec des scripts robustes.

### Travail réalisé

- Utilisation des commandes de navigation et de recherche : `pwd`, `ls`, `cd`, `find`.
- Manipulation des droits avec `chmod`, `chown` et `ls -l`.
- Étude des modèles **OSI** et **TCP/IP**, des adresses IP, des ports, du DNS et des échanges HTTP/HTTPS.
- Diagnostic réseau avec `ping`, `curl`, `ss`, `netstat`, `lsof`, les journaux système et les DevTools du navigateur.
- Écriture de scripts Bash avec `set -euo pipefail`, gestion des variables, fonctions, logs et codes de retour.
- Création des scripts `init.sh` et `run.sh` :
  - vérification des prérequis ;
  - création de `.env` depuis `.env.example` ;
  - génération de secrets locaux ;
  - construction et lancement des services Docker ;
  - migrations de la base ;
  - arrêt propre lors des signaux d'interruption.
- Modélisation du flux **client → API → PostgreSQL → fournisseur IA**, avec les ports et variables associés.

### Notions importantes

- Les services Docker communiquent par leur nom de service, par exemple `db:5432`, et non par `localhost`.
- Les variables d'environnement permettent de séparer configuration et code.
- Un script idempotent peut être relancé sans recréer inutilement l'existant.
- Les chemins doivent être relatifs au projet afin de fonctionner sur plusieurs machines.

### Livrables du Jalon 2

- Schéma d'architecture avec protocoles, ports et sens des flux.
- `scripts/init.sh` et `scripts/run.sh` exécutables.
- Liste des ports et variables dans `.env.example` ou une documentation dédiée.
- README enrichi avec les commandes de démarrage.
- Scripts validés avec `bash -n` et, si disponible, ShellCheck.

## 4. Mercredi 9 septembre — Jour 3 : conteneurisation Docker et parsing Python

### Objectif du jour

Rendre l'ingestion reproductible dans un conteneur et transformer des logs JSON ou CSV en données validées.

### Travail réalisé

- Comparaison entre machines virtuelles et conteneurs : isolation, poids, démarrage et usage.
- Prise en main de `docker pull`, `docker run`, `docker ps`, `docker logs`, `docker exec`, `docker stop` et `docker rm`.
- Écriture d'un Dockerfile Python avec image légère, dépendances installées sans cache et point d'entrée défini.
- Application du principe du moindre privilège avec un utilisateur non-root.
- Rappel Python : types, conditions, boucles, fonctions, modules et annotations.
- Création de parsers JSON et CSV.
- Validation des champs avec Pydantic : timestamp, adresses IP, port, protocole, taille et sévérité.
- Exposition d'un endpoint FastAPI `POST /logs` dans un conteneur.
- Mise en place d'un fichier `.dockerignore` pour éviter d'inclure `.git`, les caches, `.env` ou d'autres fichiers inutiles dans l'image.

### Notions importantes

- Une image doit être légère, reproductible et construite à partir de couches limitées.
- Les logs invalides doivent être rejetés clairement plutôt que stockés avec des valeurs incertaines.
- La validation doit être effectuée côté serveur, indépendamment du client.
- Les erreurs de parsing et les rejets doivent produire des journaux structurés.

### Livrables du Jalon 3

- Dockerfile fonctionnel et image construite.
- `compose.yaml` lançant le service d'ingestion.
- Parser JSON et CSV.
- Endpoint `POST /logs` répondant à un payload valide et rejetant les payloads invalides.
- Conteneur lancé en non-root, avec une image réduite et un comportement vérifiable.

## 5. Jeudi 10 septembre — Jour 4 : cyber offensive et OWASP

### Objectif du jour

Adopter une posture d'auditeur pour comprendre comment les erreurs de développement deviennent des vulnérabilités exploitables, puis transformer chaque constat en remédiation.

### Travail réalisé

- Présentation de la surface d'attaque et des catégories de l'**OWASP Top 10 2021**.
- Atelier local sur OWASP Juice Shop ou DVWA.
- Mise en pratique de plusieurs cas :
  - injection SQL et contournement de connexion ;
  - XSS réfléchi, stocké et DOM ;
  - contrôle d'accès défaillant et IDOR ;
  - CSRF et mauvaise configuration ;
  - dépendances vulnérables et fuite d'informations.
- Cartographie des entrées du projet : endpoints HTTP, paramètres, fichiers, variables d'environnement, webhooks et files de messages.
- Classement des risques selon la probabilité, l'impact et la criticité.
- Rédaction de preuves reproductibles avec prérequis, commandes, résultat observé et résultat attendu après correction.
- Création d'issues de remédiation avec référence OWASP, description, impact et correctif proposé.

### Notions importantes

- Le schéma de pensée principal est : **entrée non validée → traitement non sûr → impact**.
- Une preuve doit pouvoir être reproduite par une autre personne sans aide.
- Les tests offensifs sont réalisés uniquement sur des environnements locaux autorisés.
- Les requêtes SQL doivent être paramétrées et les sorties doivent être échappées.
- Les contrôles d'accès doivent être vérifiés côté serveur.

### Livrables du Jalon 4

- Cartographie de la surface d'attaque.
- Registre de risques priorisé.
- Au moins deux preuves de concept reproductibles.
- Issues Git de remédiation étiquetées et documentées.
- Premières corrections ou recommandations associées aux risques détectés.

## 6. Vendredi 11 septembre — Jour 5 : cyber défensive et DevSecOps

### Objectif du jour

Consolider la sécurité de l'application avant la persistance des données et l'intégration de l'IA.

### Travail réalisé

- Étude du **Secure Coding** et de l'intégration de la sécurité dans le cycle DevSecOps.
- Différenciation entre décalage à gauche (`shift-left`) et décalage à droite (`shift-right`).
- Mise en place de contrôles automatisés : validation, SAST, analyse des dépendances et scan d'image.
- Isolation des secrets avec `.env`, `.env.example`, `.gitignore` et `python-dotenv`.
- Étude du nettoyage d'un historique Git contenant des secrets, notamment avec BFG Repo Cleaner, puis rotation des valeurs compromises.
- Distinction entre hachage et chiffrement :
  - hachage adapté aux mots de passe, avec bcrypt ou Argon2 ;
  - chiffrement adapté aux données qui doivent pouvoir être retrouvées.
- Validation stricte des entrées API selon quatre niveaux :
  - type ;
  - format ;
  - longueur ;
  - valeurs autorisées par liste blanche.
- Utilisation de Pydantic pour obtenir des réponses `422 Unprocessable Entity` lorsque le contrat n'est pas respecté.
- Durcissement du conteneur : utilisateur non-root, système de fichiers en lecture seule, capacités retirées, `no-new-privileges`, répertoires temporaires contrôlés et secrets injectés au runtime.

### Notions importantes

- Toute donnée externe est considérée comme non fiable.
- Une liste blanche est plus sûre qu'une liste noire.
- Un secret présent dans l'historique Git reste exposé même après suppression du fichier.
- Les journaux ne doivent jamais contenir de token, mot de passe ou clé API.
- La sécurité doit être automatisée plutôt qu'ajoutée manuellement en fin de projet.

### Livrables du Jalon 5

- Modèle `.env.example` documenté.
- `.gitignore` vérifié.
- Entrées API strictement validées.
- Dockerfile et Compose sans secret intégré.
- Conteneur exécuté avec les privilèges minimaux.
- Recherche de secrets dans le dépôt et procédure de réaction documentée.

### Bilan de la semaine 1

La première semaine a permis de passer d'une machine non configurée à une application conteneurisée, documentée et sécurisée dans ses grands principes. Les fondations couvrent désormais Git, Linux, le réseau, Docker, Python, l'audit OWASP, la gestion des secrets et la validation des entrées.

---

# Partie 2 — Semaine 2 : données, IA, intégration et restitution

## 7. Lundi 14 septembre — Jour 6 : SQL, PostgreSQL et persistance

### Objectif du jour

Remplacer le stockage temporaire par une base PostgreSQL persistante et rendre les logs consultables et filtrables.

### Travail réalisé

- Comparaison entre bases SQL et NoSQL et justification du choix de PostgreSQL pour des données structurées et reliées.
- Modélisation des tables :
  - `logs` : événement technique, niveau, message, source, horodatage et métadonnées ;
  - `analyses` : résultat lié à un log, sévérité, catégorie, résumé, recommandations et fournisseur.
- Utilisation des clés primaires, clés étrangères, contraintes et relations `ON DELETE CASCADE`.
- Pratique des requêtes SQL fondamentales : `SELECT`, `INSERT`, `UPDATE`, `DELETE` et `JOIN`.
- Lancement de PostgreSQL dans Docker et connexion avec `psql`.
- Création d'un volume nommé pour conserver les données après arrêt ou recréation du conteneur.
- Connexion de FastAPI à PostgreSQL via `DATABASE_URL`.
- Ajout des filtres `GET /logs?level=...`, `source=...` et `limit=...`.
- Validation des paramètres avant requête et utilisation de paramètres SQL plutôt que de concaténation.
- Diagnostic des problèmes de réseau Docker avec `docker compose ps`, `docker compose logs`, `docker compose exec`, `docker network ls` et `docker inspect`.

### Notions importantes

- Un volume Docker préserve les données au-delà du cycle de vie d'un conteneur.
- Le nom du service Compose est l'adresse à utiliser entre conteneurs.
- Les index accélèrent les filtres fréquents sur le niveau, la source ou la date.
- Une requête `UPDATE` ou `DELETE` sans `WHERE` peut modifier ou supprimer toutes les lignes.

### Livrables du Jalon 6

- Tables `logs` et `analyses` créées dans PostgreSQL.
- Connexion API/BDD fonctionnelle et healthcheck positif.
- Volume `postgres_data` opérationnel.
- Test de persistance réussi après `docker compose down` puis `up`.
- Filtres API fonctionnels et sécurisés.

## 8. Mardi 15 septembre — Jour 7 : intégration de l'IA et API REST

### Objectif du jour

Analyser un log stocké pour produire une alerte structurée, sans coupler le code métier à un fournisseur IA particulier.

### Travail réalisé

- Conception d'une architecture en trois couches :
  - **fournisseur** : interface commune ;
  - **adaptateur** : OpenAI, Ollama ou autre implémentation ;
  - **schéma** : contrat de réponse validé.
- Création d'une interface `IProvider` avec une méthode d'analyse.
- Implémentation d'adaptateurs OpenAI et Ollama.
- Ajout d'un fournisseur simulé pour les tests et les démonstrations sans réseau.
- Définition d'un schéma Pydantic de diagnostic avec sévérité, catégorie, explication, indicateurs et recommandation.
- Création d'un prompt template demandant une réponse JSON stricte.
- Mise en place du service d'analyse et de l'endpoint `POST /logs/{id}/analyze`.
- Gestion des réponses invalides, des erreurs réseau, des timeouts et des retries.
- Vérification que les tests n'appellent aucun service externe.

### Notions importantes

- Le modèle IA ne doit pas être considéré comme une source de données parfaitement fiable : sa réponse doit être validée.
- Le prompt doit recevoir un log ciblé et sanitized, pas un fichier complet contenant des données sensibles.
- Le pattern fournisseur/adaptateur permet de remplacer OpenAI par Ollama ou un mock sans réécrire le service.
- Un fallback déterministe est indispensable pour les tests et la démonstration.

### Livrables du Jalon 7

- Interface commune et adaptateurs fonctionnels.
- Schéma de diagnostic validé.
- Prompt template externalisé.
- Service d'analyse et endpoint REST.
- Tests unitaires avec fournisseur simulé.
- Bascule possible entre OpenAI, Ollama et mock via configuration.

## 9. Mercredi 16 septembre — Jour 8 : sprint d'intégration globale

### Objectif du jour

Assembler les briques développées les jours précédents et obtenir une version cohérente, redémarrable et démontrable.

### Travail réalisé

- Briefing du sprint avec un objectif commun : démarrer le projet avec une seule commande Docker Compose.
- Intégration de l'API, de PostgreSQL, des scripts Bash, de la validation, des secrets et du fournisseur IA.
- Vérification progressive du flux complet :
  - healthcheck ;
  - ingestion d'un log ;
  - lecture des logs ;
  - analyse d'un log existant ;
  - consultation des alertes ;
  - exécution des tests automatisés.
- Travail en autonomie guidée avec répartition pilote/copilote.
- Documentation des blocages avec commande, message d'erreur et résultat attendu.
- Stand-up de fin de matinée : démonstration courte, état réel, blocages et plan pour le jour suivant.
- Préparation du code freeze : arrêt des nouvelles fonctionnalités, correction ciblée des anomalies et stabilisation de la version.

### Notions importantes

- L'intégration doit être testée par petits incréments, pas uniquement à la fin.
- Un blocage doit être décrit de façon reproductible pour être résolu rapidement.
- Le code freeze protège la version de démonstration contre les modifications de dernière minute.
- Un plan B, notamment le fournisseur IA simulé, réduit le risque pendant la démo.

### Livrables du jour

- Projet démarrable avec Docker Compose.
- endpoints du contrat API fonctionnels ;
- persistance PostgreSQL vérifiée ;
- analyse IA fonctionnelle avec un fournisseur réel ou simulé ;
- tests automatisés exécutés ;
- README, `.env.example` et jeu de logs de démonstration mis à jour ;
- liste des blocages et feuille de route pour la finalisation.

## 10. Jeudi 17 septembre — Jour 9 : tests, documentation et finalisation

### Objectif du jour

Transformer un projet fonctionnel en projet fiable, maintenable et prêt à être présenté.

### Travail réalisé

- Rédaction d'un README professionnel contenant description, prérequis, installation, démarrage, architecture, endpoints, tests, sécurité et dépannage.
- Écriture de tests automatisés avec pytest et `TestClient` FastAPI.
- Utilisation d'une base de test légère et d'un fournisseur IA simulé pour obtenir des tests rapides et déterministes.
- Couverture des comportements principaux : santé, authentification, logs, filtres, analyses, alertes, réponses invalides et sécurité.
- Exécution de Ruff pour détecter les imports inutilisés, les erreurs de style et les problèmes de maintenabilité.
- Correction des anomalies signalées puis nouvelle exécution des tests.
- Application du code freeze : aucune nouvelle fonctionnalité, uniquement des corrections de bugs et de la documentation.
- Finalisation des supports :
  - `README.md` ;
  - `DEMO_DAY.md` ;
  - `DEMO_SCRIPT.md` ;
  - `CI_GUIDE.md` ;
  - `PITCH.md` ;
  - jeu de commandes et données de démonstration.
- Création d'un tag Git de version pour figer l'état démontré.
- Répétition générale chronométrée, avec vérification des plans de secours et de la répartition de parole 50/50.

### Notions importantes

- Un test suit généralement les étapes **Arrange, Act, Assert**.
- Le linting complète les tests en détectant des problèmes que l'exécution ne révèle pas toujours.
- Le code freeze ne signifie pas arrêter le travail : il signifie changer de priorité vers la stabilité.
- Une démo doit raconter un scénario utilisateur complet plutôt qu'une suite d'écrans de code.

### Livrables du Jalon 8

- Suite pytest verte.
- Ruff sans erreur.
- README final et documentation de démonstration.
- Code freeze appliqué.
- Tag de version.
- Jeu de démonstration reproductible.
- Plan B testé.
- Répétition de six minutes réalisée.

## 11. Vendredi 18 septembre — Jour 10 : Demo Day et clôture

### Objectif du jour

Présenter le système complet, répondre aux questions techniques, recevoir du feedback et formaliser les apprentissages pour la suite.

### Travail réalisé

- Vérification matérielle : projecteur, partage d'écran, réseau, lancement des conteneurs, Swagger et chronométrage.
- Démonstration de six minutes par équipe suivant le parcours :
  1. contexte métier ;
  2. architecture ;
  3. ingestion d'un log ;
  4. validation et stockage ;
  5. analyse IA ;
  6. génération et consultation de l'alerte ;
  7. sécurité, tests et limites.
- Questions-réponses de quatre minutes avec le jury et la salle.
- Respect de la répartition de parole 50/50 entre les membres du binôme.
- Évaluation selon la clarté du scénario, la maîtrise technique, la fluidité de la démo, la qualité des réponses et la répartition de parole.
- Feedback croisé selon le modèle **Situation – Comportement – Impact**.
- Synthèse collective des réussites et des points de vigilance.
- Bilan personnel avec trois actions concrètes pour la rentrée : technique, méthodologique et relationnelle.
- Clôture avec recommandations sur la dette technique, la veille sécurité, les contributions open source et les certifications.

### Checklist finale du projet

- Dépôt Git propre, historique lisible, PR relues et tag de version.
- Aucun secret dans le code ou l'historique.
- API FastAPI documentée dans Swagger et démarrable par Docker Compose.
- Healthcheck et endpoints principaux opérationnels.
- PostgreSQL persistant, schéma reproductible, migrations et index présents.
- Ingestion JSON/CSV avec validation et erreurs explicites.
- Analyse structurée via OpenAI, Ollama ou mock.
- Audit de sécurité et remédiations documentés.
- Tests automatisés, README et jeu de données de démonstration.
- Démo de six minutes, Q&A de quatre minutes et plan de secours validé.

---

# Partie 3 — Architecture et flux fonctionnel final

Le projet suit le parcours suivant :

```text
Client / Swagger UI / curl
        |
        v
FastAPI — validation Pydantic et contrôles de sécurité
        |
        +--> PostgreSQL : logs et analyses persistants
        |
        +--> Fournisseur IA
        |      +-- OpenAI
        |      +-- Ollama
        |      +-- MockProvider pour les tests et la démo
        |
        v
Diagnostic structuré : sévérité, catégorie, indicateurs, recommandation
        |
        v
Alerte consultable et exploitable
```

Les composants sont orchestrés par Docker Compose. La configuration est externalisée dans `.env` ou des secrets Docker, les données PostgreSQL sont stockées dans un volume nommé et les communications entre services utilisent les noms de services plutôt que `localhost`.

## Endpoints principaux

- `GET /health` ou `/healthz` selon la version du contrat ;
- `POST /logs` ou endpoint d'ingestion équivalent ;
- `GET /logs` avec filtres ;
- `GET /logs/{id}` ;
- `POST /logs/{id}/analyze` ;
- `GET /alerts`.

Les documents sources mentionnent plusieurs ports et noms de healthcheck, notamment 5000/8000 et `/health`/`/healthz`. La version livrée doit harmoniser ces valeurs dans le README, Compose, les scripts et les tests.

---

# Partie 4 — Compétences acquises

## Compétences techniques

- Installation et prise en main d'un environnement DevSecOps complet.
- Utilisation quotidienne de Git, des branches, des commits atomiques et des Pull Requests.
- Navigation Linux, droits de fichiers et scripts Bash robustes.
- Compréhension des modèles OSI/TCP-IP, DNS, HTTP, ports et flux réseau.
- Création et durcissement d'images Docker, orchestration avec Docker Compose.
- Développement Python, parsing JSON/CSV et validation Pydantic.
- Création d'API FastAPI documentées par OpenAPI/Swagger.
- Modélisation SQL, PostgreSQL, volumes persistants, requêtes paramétrées et filtres.
- Intégration d'un LLM avec architecture fournisseur/adaptateur et réponse JSON validée.
- Tests automatisés, linting, couverture, documentation et packaging.

## Compétences sécurité

- Analyse de surface d'attaque et classification OWASP.
- Détection et remédiation des injections, XSS, IDOR, CSRF et mauvaises configurations.
- Gestion des secrets, nettoyage d'historique Git et rotation des valeurs compromises.
- Validation serveur par liste blanche et limitation des tailles de requêtes.
- Durcissement des conteneurs et application du moindre privilège.
- Séparation des environnements de développement, test et production.
- Documentation des preuves, risques et corrections.

## Compétences méthodologiques

- Peer-programming et alternance des rôles pilote/copilote.
- Travail en sprint, stand-up et autonomie guidée.
- Documentation des blocages et communication d'un état réel.
- Code freeze, gestion des régressions et versionnement.
- Préparation d'une démonstration chronométrée avec plan B.
- Feedback constructif et bilan personnel.

---

# Partie 5 — Points de vigilance relevés dans les supports

- Harmoniser les ports et le nom du healthcheck avant toute exécution finale.
- Ne pas copier-coller les exemples contenant des identifiants, tokens ou URLs sensibles.
- Ne pas lancer les commandes de nettoyage Docker ou de réécriture d'historique Git sans comprendre leur effet.
- Conserver les tests avec fournisseur simulé afin de ne pas dépendre du réseau pendant la démonstration.
- Vérifier que les secrets sont absents de l'image, du dépôt et de l'historique Git.
- Relire les documents de démonstration sur une machine propre avant le Demo Day.

---

# Conclusion

En dix jours, le binôme est passé d'un environnement à configurer à une application complète et démontrable. La progression a couvert l'ensemble du cycle DevSecOps : installation, collaboration Git, Linux et réseau, conteneurisation, développement Python, audit offensif, sécurisation défensive, persistance SQL, analyse IA, intégration, tests, documentation et restitution.

Le livrable final attendu est une version reproductible de l'API, accompagnée de sa documentation, de ses tests, de son audit de sécurité, de son jeu de données et d'une démonstration maîtrisée du parcours **log brut → validation → stockage → analyse → alerte**.

## Fichiers sources synthétisés

- `7_septembre.md`
- `8_septembre.md`
- `9_septembre.md`
- `10_septembre.md`
- `11_septembre.md`
- `14_septembre.md`
- `15_septembre.md`
- `16_septembre.md`
- `17_septembre.md`
- `18_septembre.md`
