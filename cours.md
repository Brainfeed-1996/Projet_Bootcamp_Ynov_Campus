Cahier des charges
Des logs bruts à une alerte exploitable
Construisez une API qui reçoit des événements techniques, les valide, les conserve dans PostgreSQL puis demande à OpenAI ou Ollama une analyse structurée. La démonstration finale se fait dans Swagger UI.

Architecture de référence
SourcesFichiers JSON/CSV ou requêtes HTTP
API FastAPIValidation, ingestion et consultation
PostgreSQLLogs, analyses et alertes persistantes
Moteur IAOpenAI ou Ollama derrière la même interface
SwaggerDémonstration et validation de l’API
Pour aller plus loin · rôle des outils
Commence par lire « Ce que c’est ». Le rôle dans le projet deviendra plus clair au fil des jalons.

Terminal
Ce que c’est : Une fenêtre dans laquelle on écrit des commandes pour demander des actions à l’ordinateur.

Dans ce projet : Il sert à lancer le projet, installer des outils, lire les erreurs et utiliser Git ou Docker.

Python
Ce que c’est : Un langage de programmation : il permet d’écrire les instructions suivies par l’API.

Dans ce projet : Vous l’utiliserez pour lire les logs, vérifier leur format, les enregistrer et demander une analyse IA.

Git
Ce que c’est : Un outil qui mémorise les versions successives des fichiers d’un projet.

Dans ce projet : Il permet de revenir en arrière, de travailler en branche et de réunir le travail des deux membres du binôme.

Docker
Ce que c’est : Un outil qui emballe une application et ses dépendances dans un conteneur isolé.

Dans ce projet : Le conteneur évite les différences entre les machines : le projet se lance avec les mêmes versions partout.

Docker Compose
Ce que c’est : Un fichier et une commande qui lancent plusieurs conteneurs ensemble.

Dans ce projet : Ici, il démarrera l’API FastAPI et la base PostgreSQL avec une seule commande.

API
Ce que c’est : Une interface accessible par le réseau : un programme envoie une requête et reçoit une réponse.

Dans ce projet : Votre API recevra des logs et permettra de les consulter ou de déclencher leur analyse.

FastAPI
Ce que c’est : Un framework Python qui aide à créer une API avec des routes comme GET /logs ou POST /logs.

Dans ce projet : Il organise le code serveur, vérifie les données reçues et génère la documentation de l’API.

PostgreSQL
Ce que c’est : Un logiciel de base de données relationnelle qui stocke des informations dans des tables.

Dans ce projet : Il gardera les logs et analyses après l’arrêt de l’application, afin de pouvoir les rechercher.

Swagger UI
Ce que c’est : Une page web générée par FastAPI qui liste les routes de l’API et permet de les essayer.

Dans ce projet : Elle sert à vérifier les endpoints et à faire la démonstration finale sans développer de frontend.

OpenAI ou Ollama
Ce que c’est : Deux moyens d’utiliser un modèle de langage : OpenAI est un service en ligne, Ollama peut exécuter un modèle sur la machine.

Dans ce projet : Ils transforment un log en diagnostic structuré, sous une interface commune dans votre code.

pytest
Ce que c’est : Un outil Python qui lance automatiquement des tests écrits par les développeurs.

Dans ce projet : Il vérifie que les fonctions et routes fonctionnent toujours après une modification.

.env et .env.example
Ce que c’est : Des fichiers de configuration : .env contient les valeurs locales ; .env.example montre les noms des variables à fournir.

Dans ce projet : Ils évitent de mettre des mots de passe ou clés API dans Git tout en aidant un autre membre à configurer le projet.

Contrat API minimal
GET
/health
Vérifier l’API et la connexion PostgreSQL.

POST
/logs
Valider puis enregistrer un événement de log.

GET
/logs
Lister et filtrer les logs par niveau, source et limite.

GET
/logs/{id}
Consulter un log et sa dernière analyse.

POST
/logs/{id}/analyze
Obtenir une analyse structurée avec le fournisseur IA choisi.

GET
/alerts
Lister les analyses classées comme suspectes.

Données à persister
Log
id · occurred_at · level · source · message · metadata · created_at
Analysis
id · log_id · severity · category · summary · recommendations · provider · created_at
Règles non négociables
Le dépôt démarre avec un README, un .gitignore et un .env.example sans secret.
L’application et PostgreSQL démarrent avec une seule commande Docker Compose.
Les entrées sont validées avant stockage et avant envoi à un fournisseur IA.
Aucune clé API, donnée personnelle ou donnée sensible ne doit entrer dans Git.
Le fournisseur IA est remplaçable : OpenAI et Ollama respectent le même contrat Python.
Les appels IA sont simulés dans les tests afin de rester rapides et déterministes.
La démonstration finale passe par Swagger UI et un jeu de logs reproductible.
Planning détaillé
7–11 septembre
Semaine 1 · Socle systèmes, infrastructure et début du projet
J01
Lundi 7 septembre
Positionnement, installation des environnements & Git
+
09h00–09h30
Accueil & test de positionnement
09h00–09h10 : présentation de l’organisation et des objectifs.
09h10–09h30 : QCM individuel pour cartographier les niveaux.
09h30–10h00
Constitution des binômes & peer-programming
Former des binômes mixtes : un profil avancé avec un profil débutant.
Le profil avancé guide et explique; le profil débutant garde le clavier.
10h00–11h15
Mise en place de l’environnement
Valider VS Code, Git, Python 3.10+ et Docker Desktop.
Configurer Git, générer les clés SSH et relier GitHub ou GitLab.
Résoudre les droits administrateur, WSL2 et variables PATH.
11h15–12h00
Bases de Git & jalon 1
Revoir clone, status, add, commit, push, branch et Pull Request.
Initialiser le dépôt officiel, rédiger le README et valider la première PR.
Ouvrir l’aide du jalon 1 · Dépôt et première Pull Request →
J02
Mardi 8 septembre
Linux, scripting Bash & réseau
+
09h00–09h40
CLI Linux & fondamentaux réseau
Arborescence, navigation, commandes, droits et permissions chmod/chown.
Modèles OSI/TCP-IP, adresses IP, ports, DNS, requêtes et en-têtes HTTP/HTTPS.
09h40–10h30
Manipulation CLI & inspection réseau
Manipuler les fichiers et écrire des scripts Bash d’automatisation.
Inspecter le trafic local et interroger une API avec curl, ping et les DevTools.
10h30–11h30
Fil rouge · jalon 2
Définir l’architecture réseau de Projet Bootcamp.
Écrire les scripts Bash d’initialisation et de lancement.
11h30–12h00
Débrief & Q&A
Résoudre les confusions sur chemins absolus/relatifs et variables d’environnement.
Ouvrir l’aide du jalon 2 · Architecture réseau et scripts →
J03
Mercredi 9 septembre
Conteneurisation Docker & scripting Python
+
09h00–09h40
Docker & introduction Python
Comparer machines virtuelles et conteneurs Docker.
Revoir variables, types, conditions, boucles et fonctions Python.
09h40–10h30
Premier conteneur & parser Python
Manipuler docker run, ps, logs et exec.
Créer un Dockerfile et parser un fichier de logs JSON ou CSV.
10h30–11h30
Fil rouge · jalon 3
Écrire le Dockerfile officiel.
Développer le module d’ingestion et de traitement des données.
11h30–12h00
Mini-restitution
Deux binômes présentent et comparent la structure de leur Dockerfile.
Ouvrir l’aide du jalon 3 · Ingestion et conteneurisation →
J04
Jeudi 10 septembre
Cyber offensive : sensibilisation & OWASP
+
09h00–09h40
Sensibilisation sécurité & Top 10 OWASP
Adopter la posture d’un auditeur et cartographier la surface d’attaque web.
Étudier injection SQL, XSS, CSRF, mauvaises configurations et contrôles d’accès défaillants.
09h40–11h15
Atelier CTF
Déployer localement OWASP Juice Shop ou DVWA via Docker.
Résoudre trois à quatre challenges guidés, dont injection SQL simple et XSS.
11h15–11h45
Fil rouge · jalon 4
Auditer le code et les scripts produits pendant les jours 2 et 3.
11h45–12h00
Synthèse
Relier les erreurs de code classiques aux vulnérabilités exploitables.
Ouvrir l’aide du jalon 4 · Audit d’impact →
J05
Vendredi 11 septembre
Cyber défensive & DevSecOps
+
09h00–09h40
Sécurisation & Clean Code
Étudier Secure Coding et principes DevSecOps.
Isoler les secrets avec .env et .gitignore.
Distinguer hachage bcrypt/argon2 et chiffrement.
09h40–10h30
Hardening & variables d’environnement
Nettoyer un dépôt fictif contenant des clés compromises.
Utiliser python-dotenv pour charger la configuration.
10h30–11h30
Fil rouge · jalon 5
Valider strictement les entrées et isoler les secrets dans les conteneurs.
11h30–12h00
Bilan semaine 1
Valider les acquis et ajuster les objectifs avant le week-end.
Ouvrir l’aide du jalon 5 · Sécurisation de l’application →
14–18 septembre
Semaine 2 · Data, IA et livrables du projet
J06
Lundi 14 septembre
Bases de données SQL & persistance
+
09h00–09h40
Modélisation & base SQL
Comparer SQL et NoSQL.
Étudier tables, clés primaires/étrangères et SELECT, INSERT, UPDATE, JOIN.
09h40–10h30
Requêtage SQL
Interroger une instance SQLite ou PostgreSQL exécutée sous Docker.
10h30–11h30
Fil rouge · jalon 6
Connecter l’API au conteneur PostgreSQL.
Stocker de façon structurée les événements et logs.
11h30–12h00
Débrief & Q&A
Diagnostiquer la communication inter-conteneurs et docker network.
Ouvrir l’aide du jalon 6 · Persistance PostgreSQL →
J07
Mardi 15 septembre
Intégration de l’IA & APIs REST
+
09h00–09h40
LLM & IA appliquée au développement
Intégrer un LLM via API REST avec OpenAI ou Ollama en local.
Contraindre la réponse du modèle à un JSON structuré.
09h40–10h30
Script de communication avec une IA
Analyser un rapport d’erreur et générer un diagnostic automatique.
10h30–11h30
Fil rouge · jalon 7
Analyser les logs stockés pour extraire des alertes de sécurité.
11h30–12h00
Démonstration
Tester le module avec plusieurs erreurs et tentatives d’attaque.
Ouvrir l’aide du jalon 7 · Analyse par IA →
J08
Mercredi 16 septembre
Sprint de développement · intégration globale
+
09h00–09h20
Briefing du sprint
Fixer les objectifs de livraison : Docker, Python/Bash, cyber, data et IA.
09h20–11h30
Sprint en autonomie guidée
Travailler en équipe pendant que l’intervenant agit comme Tech Lead et hotline.
11h30–12h00
Stand-up meeting
Trois minutes par groupe : démonstration, blocages et feuille de route du jour 9.
J09
Jeudi 17 septembre
Testing, documentation & finalisation
+
09h00–09h40
Qualité, packaging & tests
Construire un README professionnel avec démarrage, architecture et installation.
Découvrir tests automatisés pytest et outils de linting.
09h40–10h30
Qualification du code
Écrire un test unitaire simple et nettoyer le code avec un linter.
10h30–11h30
Fil rouge · jalon 8
Geler les fonctionnalités.
Finaliser la documentation et préparer le support Demo Day.
11h30–12h00
Répétition générale
Vérifier les démonstrations et préparer des solutions de secours.
Ouvrir l’aide du jalon 8 · Code Freeze et packaging →
J10
Vendredi 18 septembre
Restitution, Demo Day & closing
+
09h00–09h15
Accueil & vérification matérielle
Tester branchements, projecteur, réseau et chronométrage.
09h15–11h00
Soutenances
Dix minutes par équipe : six minutes de démonstration et quatre minutes de Q&A.
Répartir obligatoirement le temps de parole à 50/50 entre profils débutant et avancé.
11h00–11h30
Feedback & synthèse
Évaluation croisée, réussites techniques et retours constructifs.
11h30–12h00
Bilan & clôture
Retour d’expérience et conseils pour commencer l’année académique.
Aide par jalon
Lis d’abord l’objectif et les critères. N’ouvre les indices que lorsque le binôme est réellement bloqué.

01
JALON 1
Dépôt et première Pull Request
+
Créer un espace de travail partagé avec des règles de contribution compréhensibles par toute l’équipe.

Comprendre avant d’agir
Avant de coder, le binôme doit pouvoir partager son travail sans se transmettre des fichiers par message. Git conserve l’historique de chaque modification ; une Pull Request crée un moment de relecture avant que le code arrive dans la branche principale.

Vocabulaire à connaître
Dépôt
Le dossier du projet suivi par Git, localement puis sur GitHub ou GitLab.
Commit
Une photographie nommée d’un petit ensemble de modifications cohérentes.
Branche
Une ligne de travail séparée où l’on peut avancer sans modifier directement la version principale.
Pull Request
Une proposition pour comparer une branche à la branche principale, discuter puis fusionner le travail.
.gitignore
La liste des fichiers que Git ne doit jamais ajouter, par exemple .env, caches et environnements virtuels.
Ordre conseillé
Créer le dépôt officiel et cloner exactement cette adresse sur les deux machines.
Lire le résultat de git status avant toute commande : il indique ce que Git voit réellement.
Créer une branche dont le nom décrit une seule intention, par exemple docs/readme.
Modifier peu de fichiers, relire git diff, puis créer un commit avec un message qui décrit le changement.
Pousser la branche, ouvrir une Pull Request et faire relire au moins une personne avant la fusion.
Pour aller plus loin · Lire une Pull Request comme un filet de sécurité
Une relecture ne cherche pas seulement des fautes. Elle vérifie que le changement est compréhensible, testable et documenté. Le pilote explique ce qu’il a fait ; le copilote cherche le cas que le pilote a oublié.

Erreurs fréquentes
Ne pas travailler directement dans main : une erreur y bloque tout le binôme.
Ne pas faire un commit « final » qui mélange README, Docker, base de données et code API.
Ne jamais ajouter .env, une clé API ou un mot de passe : supprimer le fichier ensuite ne retire pas son historique Git.
Livrables attendus
Dépôt officiel du groupe
README initial
Branches de travail
Première Pull Request relue et fusionnée
Definition of Done
Chaque membre sait cloner le dépôt
git status est propre après la fusion
Le README explique le but de Projet Bootcamp
Afficher les indices progressifs
Commandes utiles à adapter
$ git clone <url-du-depot>
$ git switch -c docs/readme
$ git add README.md
$ git commit -m "docs: initialise le projet"
$ git push -u origin docs/readme
02
JALON 2
Architecture réseau et scripts
+
Rendre visible le trajet d’une requête et automatiser l’installation puis le lancement du projet.

Comprendre avant d’agir
Le projet réunit plusieurs programmes qui communiquent : un client appelle l’API, l’API échange avec la base puis éventuellement avec un fournisseur IA. Dessiner ce trajet évite de confondre une adresse, un port, un fichier de configuration et le programme qui écoute réellement.

Vocabulaire à connaître
Client
Le programme qui envoie une requête, par exemple curl, Swagger UI ou un navigateur.
Serveur
Le programme qui attend des requêtes et renvoie des réponses. Ici, FastAPI joue ce rôle.
Adresse et port
L’adresse désigne la machine ; le port distingue les programmes sur cette machine. localhost signifie « cette machine ».
HTTP
Le protocole de discussion du Web. GET lit une ressource ; POST envoie généralement une nouvelle donnée.
Variable d’environnement
Une valeur fournie au programme lors de son lancement, comme DATABASE_URL ou LLM_PROVIDER.
Ordre conseillé
Dessiner une flèche client → API → base de données → fournisseur IA, puis noter le retour dans l’autre sens.
Choisir et documenter les ports avant de les utiliser : API, base de données et éventuel service local IA.
Écrire un script de lancement depuis la racine du dépôt, sans dépendre du dossier depuis lequel la commande est exécutée.
Tester le plus petit trajet possible : démarrer l’API puis appeler GET /health avec curl.
Faire afficher par les scripts une erreur claire si Python, Docker ou un fichier de configuration manque.
Pour aller plus loin · Une requête HTTP suit un chemin précis
Une requête contient une méthode, une URL, parfois des en-têtes et un corps JSON. La réponse contient un code : 200 signifie généralement succès, 404 ressource absente, 422 données invalides et 500 erreur côté serveur. Lire ce code avant de chercher plus loin fait gagner du temps.

Erreurs fréquentes
Confondre localhost dans le terminal de l’ordinateur et localhost à l’intérieur d’un conteneur Docker.
Copier un chemin absolu propre à une machine au lieu de calculer le chemin depuis le projet.
Choisir un port déjà occupé sans vérifier quel programme l’utilise.
Livrables attendus
Schéma client → API → base → IA
Script d’initialisation
Script de lancement
Liste des ports et variables nécessaires
Definition of Done
Les scripts échouent explicitement si un outil manque
Les chemins fonctionnent depuis la racine du dépôt
Chaque port a un rôle documenté
Afficher les indices progressifs
Commandes utiles à adapter
$ pwd && ls -la
$ chmod +x scripts/*.sh
$ curl -i http://localhost:8000/health
$ ss -lntp 2>/dev/null || lsof -iTCP -sTCP:LISTEN
03
JALON 3
Ingestion et conteneurisation
+
Démarrer l’API en conteneur et transformer des logs JSON/CSV en objets validés.

Comprendre avant d’agir
Les logs viennent souvent de fichiers aux formats différents. L’API doit les transformer en objets fiables avant de les stocker. Docker permet de reproduire cet environnement sans demander à chacun d’installer PostgreSQL manuellement.

Vocabulaire à connaître
JSON
Un format texte structuré avec des objets, des listes, des chaînes, des nombres et des booléens.
CSV
Un fichier tabulaire : chaque ligne représente souvent une donnée et les colonnes sont séparées par un caractère.
Parser
Le code qui lit un format brut et le transforme en valeurs manipulables par Python.
Validation
La vérification des types, champs obligatoires, tailles et valeurs autorisées avant de poursuivre le traitement.
Image et conteneur
Une image est le modèle immuable ; un conteneur est une instance lancée à partir de ce modèle.
Ordre conseillé
Préparer trois logs connus : un valide, un incomplet et un clairement invalide.
Séparer lecture du fichier, transformation, validation et sauvegarde dans des fonctions distinctes.
Faire démarrer un seul service API dans Docker avant d’ajouter PostgreSQL.
Ajouter le fichier compose.yaml pour lancer API et base avec docker compose up --build.
Vérifier docker compose ps, puis lire les logs du service qui échoue au lieu de relancer au hasard.
Pour aller plus loin · Docker Compose décrit des services, pas seulement des commandes
Dans compose.yaml, chaque service reçoit un nom, une image ou un build, des variables d’environnement et parfois un volume. docker compose up construit et démarre les services ; docker compose logs montre leur sortie ; docker compose exec exécute une commande dans un service déjà lancé.

Erreurs fréquentes
Faire confiance à un JSON simplement parce qu’il est syntaxiquement valide : ses champs peuvent rester incomplets ou incohérents.
Mélanger la lecture d’un fichier, les règles métier et les requêtes SQL dans une seule grande fonction.
Mettre une clé API dans le Dockerfile : une image peut être partagée ou conservée longtemps.
Livrables attendus
Dockerfile de l’API
compose.yaml initial
Parser Python JSON/CSV
Endpoint POST /logs
Definition of Done
docker compose up --build démarre sans manipulation manuelle
Un fichier valide est importé
Une ligne invalide produit une erreur lisible
Afficher les indices progressifs
Commandes utiles à adapter
$ docker compose up --build
$ docker compose ps
$ docker compose logs -f api
$ docker compose exec api python -m app.import_logs samples/events.json
04
JALON 4
Audit d’impact
+
Observer le projet comme un auditeur et transformer les constats en actions concrètes.

Comprendre avant d’agir
Auditer ne consiste pas à « hacker ». Il s’agit d’observer méthodiquement où les données entrent, qui peut agir, ce qui est affiché et ce qui arrive lorsqu’une erreur survient. Le but est de produire des constats utiles et reproductibles, uniquement dans l’environnement local autorisé.

Vocabulaire à connaître
Surface d’attaque
L’ensemble des points par lesquels un utilisateur ou un programme peut interagir avec le système.
Entrée
Toute donnée reçue : corps JSON, paramètre d’URL, en-tête, fichier ou variable d’environnement.
Risque
La combinaison d’une cause possible, de sa probabilité et de son impact.
Preuve reproductible
Une suite d’étapes assez précise pour qu’une autre personne constate le même comportement dans le même environnement.
Remédiation
La modification qui réduit le risque : validation, contrôle d’accès, masquage d’erreur ou configuration plus sûre.
Ordre conseillé
Lister les routes, les entrées reçues et les données stockées avant de lancer un test.
Choisir un scénario local simple, par exemple un champ trop long ou mal formé.
Noter l’entrée envoyée, la réponse obtenue, l’impact et le comportement attendu.
Créer une issue Git courte avec une correction proposée et un critère de validation.
Refaire la même preuve après correction pour vérifier que le risque est bien réduit.
Pour aller plus loin · Un bon constat est actionnable
Une fiche de risque répond à quatre questions : quelle entrée déclenche le problème, quel impact est possible, quelle preuve locale le montre et quelle correction est attendue. Une liste de mots-clés sans scénario ne permet pas à l’équipe de prioriser.

Erreurs fréquentes
Tester une adresse publique, une machine d’un tiers ou un compte réel : cela sort du cadre du cours.
Confondre une erreur 500 avec une preuve complète de vulnérabilité : il faut identifier la donnée, l’impact et une correction.
Conserver dans une capture un secret, une donnée personnelle ou un identifiant réel.
Livrables attendus
Cartographie de la surface d’attaque
Liste priorisée de risques
Deux preuves reproductibles en local
Issues Git de remédiation
Definition of Done
Chaque risque associe entrée, impact et correction
Les tests offensifs ciblent uniquement les environnements autorisés
Les secrets et données réelles sont absents des preuves
Afficher les indices progressifs
Commandes utiles à adapter
$ curl -i -X POST http://localhost:8000/logs -H "Content-Type: application/json" --data @samples/event.json
$ docker compose logs --tail=100 api
05
JALON 5
Sécurisation de l’application
+
Corriger les risques prioritaires et isoler complètement les secrets.

Comprendre avant d’agir
La sécurité de l’application commence par réduire ce qu’elle accepte et protéger ce qu’elle connaît. Une API doit traiter toute entrée comme non fiable, même lorsqu’elle vient de son propre frontend ou d’un outil de démonstration.

Vocabulaire à connaître
Secret
Valeur qui doit rester privée : mot de passe, jeton, clé API ou URL de base contenant un mot de passe.
Configuration
Valeur qui change selon la machine ou l’environnement, sans modifier le code source.
Liste blanche
Règle qui accepte uniquement les valeurs prévues au lieu d’essayer de bloquer toutes les valeurs dangereuses.
Journalisation
Les messages écrits par l’application pour expliquer ce qui se passe. Ils ne doivent pas contenir de secrets.
Moindre privilège
Donner à un programme seulement les droits dont il a besoin pour sa tâche.
Ordre conseillé
Définir les champs attendus, leur type, leur taille maximale et les valeurs autorisées.
Faire rejeter les entrées invalides avec un message utile, sans exposer la structure interne du serveur.
Créer .env.example avec des valeurs fictives et s’assurer que .env est ignoré par Git.
Rechercher les secrets dans l’arbre Git avant chaque démonstration.
Vérifier la configuration finale de Compose avant de lancer les services.
Pour aller plus loin · Valider tôt réduit les cas à gérer
Une validation efficace se fait au bord de l’application : type correct, champ obligatoire, longueur raisonnable et valeurs permises. FastAPI peut appliquer ces contrats aux corps JSON et répondre clairement lorsque les données ne les respectent pas.

Erreurs fréquentes
Utiliser une clé API dans un exemple de README ou dans un test.
Journaliser tout le corps d’une requête alors qu’il peut contenir des informations sensibles.
Valider uniquement dans le navigateur : une requête HTTP peut contourner l’interface utilisateur.
Livrables attendus
Validation stricte des entrées
.env.example documenté
.gitignore vérifié
Configuration Docker sans secret dans l’image
Definition of Done
Une entrée trop longue ou mal formée est rejetée
git grep ne retrouve aucune clé
Le conteneur reçoit sa configuration à l’exécution
Afficher les indices progressifs
Commandes utiles à adapter
$ git grep -nE "(api[_-]?key|password|secret)" -- . ":(exclude).env.example"
$ docker compose config
$ git check-ignore -v .env
06
JALON 6
Persistance PostgreSQL
+
Stocker durablement les logs et analyses dans un service PostgreSQL séparé.

Comprendre avant d’agir
Une liste Python disparaît quand le programme s’arrête. PostgreSQL conserve les données dans une base dédiée, où les logs et leurs analyses peuvent être liés, filtrés et retrouvés plus tard.

Vocabulaire à connaître
Table
Une collection de lignes ayant les mêmes colonnes, comparable à une feuille de calcul structurée.
Ligne
Un enregistrement concret, par exemple un log reçu à un instant donné.
Clé primaire
L’identifiant unique d’une ligne, souvent nommé id.
Clé étrangère
Une colonne qui relie une ligne à une autre table, par exemple analysis.log_id vers log.id.
Volume Docker
Un espace de stockage conservé par Docker même si le conteneur de la base est recréé.
Ordre conseillé
Dessiner d’abord les deux tables Log et Analysis avec leurs champs et leur relation.
Démarrer PostgreSQL dans Compose avec un volume nommé.
Placer DATABASE_URL dans .env, jamais directement dans le code.
Créer un log, arrêter puis relancer les services et vérifier que ce log existe toujours.
Ajouter les filtres GET /logs un par un et tester chaque cas avec des données connues.
Pour aller plus loin · La persistance se vérifie par un redémarrage
Voir une donnée juste après son insertion ne prouve pas qu’elle est durable. Le test utile consiste à redémarrer les services, puis à relire la même donnée. Les requêtes doivent utiliser des paramètres afin que les valeurs restent des données et ne deviennent jamais du code SQL.

Erreurs fréquentes
Construire une requête SQL en collant directement une valeur fournie par un utilisateur.
Oublier le volume et perdre les données après la recréation du conteneur.
Créer trop de tables et de champs avant d’avoir validé le chemin minimal : recevoir, stocker, relire.
Livrables attendus
Tables logs et analyses
Connexion par variable DATABASE_URL
Volume persistant
Filtres GET /logs
Definition of Done
Les données survivent au redémarrage des conteneurs
L’API attend que la base soit disponible
Les requêtes utilisent des paramètres, jamais de concaténation SQL
Afficher les indices progressifs
Commandes utiles à adapter
$ docker compose exec db psql -U bootcamp -d bootcamp
$ docker compose restart
$ curl "http://localhost:8000/logs?level=ERROR&limit=10"
07
JALON 7
Analyse par IA
+
Transformer un log en diagnostic JSON structuré sans coupler l’API à un fournisseur unique.

Comprendre avant d’agir
Le modèle IA est un fournisseur parmi d’autres : l’API ne doit pas dépendre de sa réponse exacte pour fonctionner. Le projet demande donc une interface commune, un schéma de sortie contrôlé et un faux fournisseur pour les tests.

Vocabulaire à connaître
Fournisseur
Le service ou logiciel qui exécute le modèle, par exemple OpenAI ou Ollama.
Adaptateur
Une petite couche de code qui traduit l’interface commune du projet vers un fournisseur précis.
Prompt
Les instructions et données envoyées au modèle pour demander une réponse.
Schéma
La forme attendue d’une réponse : ici sévérité, catégorie, résumé et recommandations.
Faux fournisseur
Une implémentation locale prévisible qui imite le contrat sans appeler une vraie IA.
Ordre conseillé
Écrire la structure JSON attendue avant de choisir OpenAI ou Ollama.
Définir une interface Python qui reçoit un log et retourne exactement cette structure.
Créer un faux fournisseur qui renvoie une réponse fixe et cohérente.
Brancher un seul vrai fournisseur derrière cette interface, avec sa configuration dans .env.
Valider la réponse reçue avant de l’enregistrer dans PostgreSQL ou de l’afficher.
Pour aller plus loin · Une IA reste une dépendance externe
Un fournisseur peut répondre lentement, échouer ou produire un format inattendu. Une application robuste prévoit ces cas : délai d’attente, message d’erreur lisible, validation du schéma et tests fondés sur un faux fournisseur déterministe.

Erreurs fréquentes
Envoyer tout un fichier de logs alors que seuls quelques champs sont nécessaires au diagnostic.
Supposer qu’un modèle répondra toujours un JSON valide.
Faire dépendre les tests d’un réseau, d’un quota ou d’une clé API réelle.
Livrables attendus
Interface commune de fournisseur
Adaptateur OpenAI ou Ollama
Schéma de réponse validé
Endpoint POST /logs/{id}/analyze
Definition of Done
La sortie contient sévérité, catégorie, résumé et recommandations
Une réponse IA invalide est gérée proprement
Les tests utilisent un faux fournisseur local
Afficher les indices progressifs
Commandes utiles à adapter
$ curl -X POST http://localhost:8000/logs/1/analyze
$ docker compose logs -f api
08
JALON 8
Code Freeze et packaging
+
Stabiliser une version démontrable, testée et documentée.

Comprendre avant d’agir
Le Code Freeze fixe une version démontrable. À ce stade, l’objectif n’est plus d’ajouter des idées : il est de rendre le projet simple à installer, prévisible à lancer et clair à expliquer en six minutes.

Vocabulaire à connaître
Régression
Un comportement qui fonctionnait auparavant mais qui est cassé par une modification récente.
Test automatisé
Un programme qui vérifie un résultat attendu sans intervention manuelle.
Version
Un état identifié du projet, par exemple v1.0-demo, auquel on peut revenir.
Tag Git
Une étiquette posée sur un commit précis pour marquer une version importante.
Plan B
Une solution de secours préparée pour poursuivre la démonstration si une dépendance échoue.
Ordre conseillé
Arrêter d’ajouter des fonctionnalités et lister ce qui doit réellement être montré.
Exécuter les tests, puis refaire le démarrage depuis une machine ou un environnement propre.
Préparer un jeu de logs de démonstration court, stable et sans donnée sensible.
Répéter la démonstration avec le chronomètre et attribuer une partie à chaque membre du binôme.
Créer le tag final uniquement lorsque README, tests et démonstration sont alignés.
Pour aller plus loin · Une bonne démonstration raconte un trajet
La démonstration la plus claire part d’un log connu, montre son ingestion, sa persistance puis son analyse et se termine par une alerte filtrée. Chaque étape doit répondre à une question simple : qu’envoie-t-on, où va la donnée et comment vérifie-t-on le résultat ?

Erreurs fréquentes
Modifier le cœur du projet juste avant la démonstration sans rejouer les tests.
Dépendre d’une réponse IA en direct sans prévoir de réponse enregistrée ou de faux fournisseur.
Présenter le code écran par écran au lieu de montrer un scénario utilisateur complet.
Livrables attendus
Tests automatisés
README final
Jeu de démonstration
Tag de version et support Demo Day
Definition of Done
Le projet repart sur une machine propre
Les tests passent sans accès à une vraie IA
La démonstration tient en six minutes
Le temps de parole est réparti à 50/50
Afficher les indices progressifs
Commandes utiles à adapter
$ pytest -q
$ docker compose up --build -d
$ docker compose ps
$ git tag -a v1.0-demo -m "Demo Day"
Cadre éthique des ateliers cyber
Les manipulations offensives sont limitées aux applications vulnérables lancées localement pour le cours. Aucun scan, test ou contournement ne doit viser un service public ou un système sans autorisation explicite.

Livrables & Demo Day
Checklist de sortie
01
Dépôt Git propre avec historique lisible et Pull Requests relues.

02
API FastAPI documentée dans Swagger et démarrable via Docker Compose.

03
PostgreSQL persistant avec schéma reproductible.

04
Ingestion de logs JSON ou CSV avec validation et erreurs explicites.

05
Analyse structurée via OpenAI ou Ollama, remplaçable et testable hors ligne.

06
Audit de sécurité et remédiations prioritaires documentés.

07
Tests automatisés, README de démarrage et jeu de données de démonstration.

08
Démo de six minutes suivie de quatre minutes de questions, parole répartie à 50/50.