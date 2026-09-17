# Narration orale — "Des logs bruts à une alerte exploitable"
## Présentation vidéo (10–12 minutes)

---

## Diapositive 1 — Titre (00:30)

Bonjour à tous ! Vous recevez un tas de logs techniques, et votre responsable vous demande… « Et bien sûr qu’il y ait une alerte exploitable à la fin. »  
C’est ce que l’on va construire : **passer des logs bruts à une alerte exploitable**.  
Je m’appelle Scott, et avec mes collègues, on va vous guider pendant **10 jours** — du 7 au 18 septembre — dans la construction d’une **API FastAPI** qui ingère des logs, les stocke dans **PostgreSQL**, puis demande à un **modèle d’IA** — OpenAI ou Ollama — de produire une analyse structurée.  
Et le tout, en **DevSecOps** : on intègre la sécurité dès le départ.  
À la fin, vous présenterez une démo de 6 minutes, suivie de 4 minutes de questions.  
C’est parti pour la première diapositive : **l’architecture de référence**.

---

## Diapositive 2 — Architecture de référence (00:45)

Avant d’écrire une seule ligne de code, on dessine le tableau d’ensemble. Imaginez **trois couches** qui se parlent en cascade.  
La **première couche**, en haut, c’est **les sources** : fichiers JSON, CSV, ou requêtes HTTP. Ce sont les **logs bruts**, parfois mal formatés, parfois incomplets.  
La **deuxième couche**, le **cœur du système**, c’est **l’API FastAPI**. Elle reçoit les logs, les **valide**, les **persiste**, et sert d’interface via Swagger UI.  
Et la **troisième couche**, en bas : **PostgreSQL** conserve les logs et analyses. Le **moteur IA** les transforme en diagnostic structuré : sévérité, catégorie, résumé, recommandations.  
Chaque couche évoluera indépendamment — on peut remplacer PostgreSQL ou Ollama sans tout casser.  
C’est ce même schéma qu’on va réaliser concrètement. Passons à la liste des outils.

---

## Diapositive 3 — Les outils du projet (00:50)

Voici **l’arsenal** du projet. Vous n’avez pas besoin de tout connaître, mais de **reconnaître chaque nom**.  
**Terminal et ligne de commande**, **Python** pour la logique, **Docker** pour empaqueter, **FastAPI** pour l’API, **PostgreSQL** pour la base, **Swagger UI** pour tester, **OpenAI ou Ollama** pour l’IA, **pytest** pour les tests, et **Git** pour la collaboration.  
Petite note sur **.env** et **.env.example** : ce sont des fichiers qui **gardent les secrets hors du code**.  
Et l’outil le plus sous-estimé ? **curl** et **docker compose**. On les utilisera presque tous les jours.  
C’est ce que fait le planning de la Semaine 1.

---

## Diapositive 4 — Planning Semaine 1 (00:40)

La **Semaine 1**, du **7 au 11 septembre**, c’est le **socle** : systèmes, infrastructure, bases du projet.  
On avance **jour par jour, en binôme**, avec le **peer-programming** : un profil avancé guide, un profil débutant manipule.  
Lundi : installation, Git, création du dépôt et première Pull Request. Règle : ne jamais committer .env ou clés API.  
Mardi : Linux, Bash, réseau — CLI, chmod, modèle OSI, scripts, curl.  
Mercredi : Docker et Python — conteneurs, Dockerfile, parser de logs.  
Jeudi : CTF offensive — Top 10 OWASP, Juice Shop ou DVWA.  
Vendredi : cyber défensive — validation, secrets, hachage bcrypt.  
À chaque fin de journée, on valide un jalon. On commence lundi par Git.

---

## Diapositive 5 — J01 — Lundi 7 septembre (00:40)

Lundi, c’est **le jour zéro**. Avant de coder, on **travaille ensemble**.  
On commence par un **test de positionnement** pour cartographier les niveaux et **répartir les binômes** — un avancé, un débutant. Le rôle du premier ? **Expliquer**, pas prendre le clavier.  
Ensuite, on installe **VS Code, Git, Python 3.10+, Docker Desktop**, on configure Git, on génère les **clés SSH**, on relie à GitHub ou GitLab.  
Puis vient la partie Git : clone, status, add, commit, push, branch, Pull Request.  
On crée le dépôt, on rédige le README, et on valide la **première Pull Request**.  
Règle importante : **ne jamais committer .env, une clé API, ou un mot de passe**. Même supprimé, l’historique Git le garde.  
À mardi, on passe à **Linux et Bash**.

---

## Diapositive 6 — J02 — Mardi 8 septembre (00:40)

Mardi, c’est **Linux, Bash, et réseau**.  
On commence par la **CLI Linux** : arborescence, navigation, droits avec **chmod et chown**.  
Ensuite, les **fondamentaux réseau** : modèle OSI/TCP-IP, IP, ports, DNS, requêtes et en-têtes HTTP. C’est crucial : derrière chaque appel à l’API, il y a une **requête HTTP**.  
Dans la pratique, on manipule des fichiers, on écrit des **scripts Bash**, et on inspecte le trafic avec **curl, ping**, et les DevTools.  
On définit aussi **l’architecture réseau** du projet et les **scripts de lancement**.  
Erreur fréquente : **confondre localhost dans le terminal et localhost dans un conteneur Docker**. À l’intérieur d’un conteneur, `localhost` ne pointe pas vers votre machine.  
À mercredi, on entre dans **Docker**.

---

## Diapositive 7 — J03 — Mercredi 9 septembre (00:40)

Mercredi, on parle de **conteneurisation Docker** et de **Python**.  
On comprend la différence entre une **machine virtuelle** et un **conteneur Docker** : un conteneur est plus léger, partage le noyau, et démarre plus vite.  
On revoit les **bases de Python** : variables, types, conditions, boucles, fonctions.  
Ensuite, on écrit un **Dockerfile**, on crée un **parser Python** pour lire des logs JSON ou CSV, et on transforme un fichier brut en **objet validé**.  
On utilise **docker compose** pour lancer l’API et PostgreSQL avec une commande.  
Règle clé : **docker compose up --build doit démarrer sans manipulation manuelle**.  
À jeudi, on **joue les attaquants**.

---

## Diapositive 8 — J04 — Jeudi 10 septembre (00:40)

Jeudi, on passe à l’offensive. On adopte la posture d’un auditeur : on cherche les failles.  
On étudie le **Top 10 OWASP**, puis on déploie localement **OWASP Juice Shop** ou **DVWA** et on résout 3-4 **challenges CTF** guidés.  
L’objectif : **lier les erreurs de code aux vulnérabilités exploitables** — exercice strictement local.  
On audite aussi le code des jours précédents et on écrit une **fiche de risque** : entrée, impact, preuve, correction.  
À vendredi, on **corrige** tout ça.

---

## Diapositive 9 — J05 — Vendredi 11 septembre (00:40)

Vendredi, on sécurise. Leçon : **on priorise, on ne tente pas de tout réparer**.  
On commence par le **Secure Coding** : validation des entrées au plus tôt — types, tailles, listes blanches. FastAPI applique ces contrats aux corps JSON.  
On isole les **secrets** avec `.env` et `.gitignore`, et on parle **hachage vs chiffrement** : un mot de passe, on le **hache** avec bcrypt — jamais en clair.  
Dans la pratique, on **nettoie un dépôt fictif** contenant des clés compromises, et on vérifie avec `git grep` qu’aucune fuite ne reste.  
C’est la **fin de la Semaine 1** : une base solide, documentée, et **sécurisée**.  
On passe maintenant à la **donnée et l’IA**.

---

## Diapositive 10 — Planning Semaine 2 (00:25)

La **Semaine 2**, du 14 au 18 septembre, c’est **l’aboutissement**.  
Lundi : PostgreSQL. Mardi : IA. Mercredi-jeudi : sprint, tests, documentation. Vendredi : Demo Day.  
Le rythme est soutenu, mais on est dans le même bateau. On commence par PostgreSQL.

---

## Diapositive 11 — J06 — Lundi 14 septembre (00:25)

Lundi, on parle de **persistance SQL**. Pourquoi passer de Python à PostgreSQL ? Parce qu’une liste en mémoire **disparaît quand le programme s’arrête**.  
PostgreSQL **garde les données dans des tables**, avec clés primaires et étrangères.  
Dans la pratique, on **dessine d’abord les tables** `Log` et `Analysis`, avec leur relation `analysis.log_id` vers `log.id`.  
On démarre PostgreSQL avec un **volume nommé** — attention, **oublier le volume, c’est perdre les données**.  
On place `DATABASE_URL` dans `.env`, jamais dans le code.  
Et on **crée un log, arrête les services, les relance, et retrouve le log intact** — c’est la **preuve de persistance**.  
On ajoute aussi les **filtres GET /logs**.  
À mardi, on **branche l’IA**.

---

## Diapositive 12 — J07 — Mardi 15 septembre (00:25)

Mardi, c’est le **cœur du projet** : **l’intégration de l’IA**.  
Point crucial : **le modèle IA est un fournisseur parmi d’autres** — on ne dépend pas de sa réponse exacte.  
On écrit d’abord la **structure JSON attendue** — sévérité, catégorie, résumé, recommandations — puis on définit une **interface Python commune**.  
On crée un **faux fournisseur** — une réponse fixe, prévisible, sans vraie IA.  
Ensuite, on branche **OpenAI ou Ollama** derrière cette interface, via `.env`, et **valide chaque réponse** : un modèle peut renvoyer un format inattendu.  
**Une IA reste une dépendance externe** — lente, échouable. On prévoit : délai, message d’erreur, validation, tests avec faux fournisseur.  
Mercredi-jeudi, c’est le **sprint final**.

---

## Diapositive 13 — J08-J09 — Sprint, tests, documentation (00:25)

Mercredi-jeudi, c’est **le sprint**. On a vu toutes les briques ; il est temps de **réunir le tout**.  
Mercredi, briefing du sprint, puis travail en équipe avec un **Tech Lead et hotline**. Stand-up de 11h30 : 3 minutes par groupe.  
Jeudi, c’est la **qualité** : README professionnel, **tests pytest**, outils de **linting**. On écrit un test unitaire, on nettoie le code, et surtout, on **gèle les fonctionnalités**.  
À 11h30, **répétition générale** : on vérifie les démonstrations et on prépare des **solutions de secours**.  
Règle : **on stabilise, on ne développe plus**.  
À vendredi, la **présentation finale**.

---

## Diapositive 14 — J10 — Vendredi 18 septembre (00:25)

Vendredi 18, c’est le **Demo Day**.  
9h-9h15 : vérification du matériel — projecteur, réseau, chronométrage.  
9h15-11h : **soutenances** — 10 minutes par équipe : 6 minutes de démo, 4 minutes de Q&A.  
Et surtout : **50/50 du temps de parole** entre les deux membres. Personne ne se contente d’assister.  
11h-11h30 : **feedback & synthèse**.  
11h30-12h : **bilan & clôture**.  
Consultez **DEMO.md** pour le déroulé exact. Mais avant, validons le **contrat API**.

---

## Diapositive 15 — Contrat API minimal (00:50)

Voici **6 endpoints**, pas une de plus.  
**GET /health** : état de l’API et connexion PostgreSQL.  
**POST /logs** : valider et enregistrer un log.  
**GET /logs** : lister et filtrer par niveau, source, limite.  
**GET /logs/{id}** : consulter un log et sa dernière analyse.  
**POST /logs/{id}/analyze** : analyse structurée — sévérité, catégorie, résumé, recommandations.  
**GET /alerts** : lister les analyses suspectes — **notre alerte exploitable**.  
Tables : **Log** — `id, occurred_at, level, source, message, metadata, created_at`. **Analysis** — `id, log_id, severity, category, summary, recommendations, provider, created_at`.  
Règle : **on ne crée pas 15 endpoints**. On garde ce contrat minimal, documenté dans Swagger.

---

## Diapositive 16 — Règles non négociables (01:00)

La sécurité, **on ne la discute pas**. Voici **les règles non négociables**.  
Première : **dépôt avec README, .gitignore, .env.example sans secret**.  
Deux : **l’appli et PostgreSQL démarrent avec une commande** — `docker compose up --build`.  
Troisième : **entrées validées avant stockage et avant envoi à l’IA**.  
Quatrième : **aucune clé API ou donnée sensible dans Git** — on vérifie avec `git grep`.  
Cinquième : **le fournisseur IA est remplaçable** — OpenAI et Ollama respectent le même contrat Python.  
Sixième : **appels IA simulés dans les tests** — faux fournisseur, pas de réseau.  
Septième : **démo par Swagger UI et jeu de logs reproductible**.  
Voyons la **definition of done**.

---

## Diapositive 17 — Definition of Done & Checklist (01:00)

Et voilà la **dernière étape**. On check la **liste de sortie** : 8 points, tous validés.  
Premier : **dépôt Git propre**, historique lisible, Pull Requests relues.  
Deux : **API FastAPI dans Swagger**, démarrable via Docker Compose.  
Troisième : **PostgreSQL persistant** avec schéma reproductible.  
Quatrième : **ingestion JSON/CSV** avec validation et erreurs explicites.  
Cinquième : **analyse structurée via OpenAI ou Ollama**, remplaçable, testable hors ligne.  
Sixième : **audit de sécurité et remédiations documentés**.  
Septième : tests automatisés, README, jeu de données de démonstration.  
Huitième : démo de 6 minutes + Q&A, parole à 50/50.  
C’est une checklist, on la respecte. Si un point est rouge, on **remonte, on corrige, on relance**.  
Voilà, vous avez **toute la carte du territoire**. Il ne reste plus qu’à **jouer**.  
Le but n’est pas d’être parfait dès le premier jour. C’est de **progresser chaque jour, en binôme, avec rigueur et curiosité**.  
Alors, on commence quand ?