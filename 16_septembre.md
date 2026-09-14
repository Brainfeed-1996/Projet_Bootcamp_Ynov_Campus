# Jour 8 - Mercredi 16 septembre : Sprint d'intégration globale

## Résumé exécutif

Le Jour 8 marque le point culminant de la semaine 2 « Data, IA et livrables du projet ». C'est le **sprint d'intégration** où toutes les fonctionnalités développées pendant les jours 6 et 7 (persistance PostgreSQL, analyse IA, APIs REST) sont assemblées, testées et stabilisées. L'objectif est d'atteindre un **Code Freeze** : une version démontrable, testée et documentée, prête pour les jours 9 (tests, documentation, finalisation) et 10 (Demo Day).

Ce jour est crucial car il transforme des briques techniques isolées en un produit cohérent. C'est aussi le moment où les équipes mesurent leur capacité à travailler en autonomie guidée, à gérer des blocages et à tenir un deadline.

---

## Pourquoi ce jour est important

Aujourd'hui, vous quittez la phase de développement de modules isolés pour entrer dans la phase d'**assemblage global**. Jusqu'à hier, vous avez travaillé sur des briques :
- **Jour 6** : persistance PostgreSQL (logs et analyses en base)
- **Jour 7** : intégration IA (analyse structurée via OpenAI ou Ollama)

Aujourd'hui, il s'agit de **relier ces briques** pour qu'elles fonctionnent ensemble comme un produit fini. C'est la différence entre avoir des morceaux de code qui marchent séparément et avoir un système qui tient la route de bout en bout.

### L'analogie de la maison

Imaginez que vous construisez une maison :
- **Jour 6**, vous avez fait les fondations (PostgreSQL).
- **Jour 7**, vous avez installé l'électricité et la plomberie (l'IA).
- **Aujourd'hui (Jour 8)**, vous posez les murs, les portes et les fenêtres : tout est relié, vous pouvez maintenant y vivre (démontrer l'API).

Sans cette journée, vous auriez des fondations et de l'électricique, mais pas de maison.

---

## Objectifs pédagogiques

À la fin de cette journée, vous devrez être capable de :

1. **Intégrer** toutes les fonctionnalités (API + base de données + IA) dans un environnement cohérent (Docker Compose).
2. **Stabiliser** une version démontrable : le projet doit redémarrer proprement et répondre de manière prévisible.
3. **Tester** l'ensemble du flux : ingestion → stockage → analyse → alerte.
4. **Documenter** les blocages et progresser en équipe de manière autonome.
5. **Préparer** la démonstration des jours 9 et 10 (code freeze, README, support Demo Day).
6. **Travailler en autonomie guidée** : l'intervenant agit comme Tech Lead et hotline, vous apprenez à vous auto-organiser.
---

## Détaillage horaire

### 09h00-09h20 — Briefing du sprint (20 minutes)

#### Objectif de cette séance

Fixer les objectifs de livraison pour cette journée de sprint. C'est le moment où l'intervenant (Tech Lead) explique ce qui doit être livré à la fin de la journée et pourquoi.

#### Ce qui se passe

L'intervenant présente les objectifs concrets :
- **Docker** : le projet doit démarrer avec une seule commande (`docker compose up --build`)
- **Python/Bash** : tous les scripts d'initialisation et de lancement doivent fonctionner
- **Cyber** : les secrets doivent être isolés, la validation stricte active
- **Data** : les logs et analyses doivent être persistés et consultables
- **IA** : l'analyse doit fonctionner avec un fournisseur (fake ou réel)

#### Pourquoi c'est important

Sans ce briefing, chaque binôme pourrait poursuivre des objectifs différents. Le sprint d'intégration nécessite une vision commune du « fait » : à quoi ressemble le projet terminé à la fin de la journée ?

#### Conseil pour le binôme

Posez des questions maintenant si vous ne comprenez pas un objectif. C'est 20 minutes qui éviteront 2 heures de travail dans la mauvaise direction.

---

### 09h20-11h30 — Sprint en autonomie guidée (2h10)

#### Objectif de cette séance

C'est le cœur de la journée : vous travaillez en équipe pour intégrer tout ce qui a été développé. L'intervenant agit comme un **Tech Lead** (il donne des conseils, aide à résoudre les problèmes architecturaux) et une **hotline** (il répond aux questions techniques).

#### Ce qui se passe

Chaque binôme travaille sur son projet. L'intervenant se déplace, écoute, aide :
- Si vous êtes bloqués sur un problème technique, il vous aide à le diagnostiquer
- Si vous ne savez pas par où commencer, il vous donne une stratégie
- Si vous avez terminé tôt, il vous propose des améliorations ou des tests supplémentaires

#### Le concept d'autonomie guidée

L'autonomie guidée signifie que vous êtes **responsables de votre progression**, mais que vous avez un **sécurité** : l'intervenant est là si vous êtes truly bloqués. C'est un équilibre entre :
- **Indépendance** : vous organisez vous-mêmes votre travail
- **Support** : vous pouvez demander de l'aide à tout moment

#### Conseils pratiques pour le sprint

1. **Commencez par le plus simple** : faites d'abord fonctionner `docker compose up --build`, puis testez chaque endpoint un par un.
2. **Testez à chaque étape** : ne codez pas 50 lignes puis testez tout à la fin. Testez après chaque modification.
3. **Documentez vos blocages** : si vous êtes bloqués, notez exactement ce qui ne marche pas avant de demander de l'aide. Plus votre description est précise, plus l'intervenant pourra vous aider rapidement.
4. **Travaillez en binôme efficacement** : alternez entre le pilote (qui écrit le code) et le copilote (qui relit, teste, cherche les erreurs). Puisque vous êtes deux, l'un peut tester pendant que l'autre code.
5. **Ne restez pas isolés** : si vous êtes bloqués depuis 10 minutes, demandez de l'aide. Les blocages coûtent plus de temps qu'ils ne semblent.

#### Plan type pour le sprint

| Étape | Action | Durée estimée |
|-------|--------|---------------|
| 1 | `docker compose up --build` : vérifier que tout démarre | 5 min |
| 2 | `GET /health` : vérifier l'API et la base | 2 min |
| 3 | `POST /logs` : créer un log de test | 5 min |
| 4 | `GET /logs` : lister les logs | 3 min |
| 5 | `GET /logs/{id}` : consulter un log | 3 min |
| 6 | `POST /logs/{id}/analyze` : analyser avec l'IA | 5 min |
| 7 | `GET /alerts` : lister les alertes | 3 min |
| 8 | Vérifier les tests (`pytest`) | 5 min |
| 9 | Lire les logs Docker pour identifier les erreurs | 5 min |
| 10 | Corriger les problèmes identifiés | variable |
| 11 | Refaire les tests | 5 min |
| 12 | Documenter l'état d'avancement pour le stand-up | 5 min |

---

### 11h30-12h00 — Stand-up meeting (30 minutes)

#### Objectif de cette séance

Chaque binôme présente son état d'avancement en 3 minutes : démonstration, blocages et feuille de route pour le jour 9.

#### Ce qui se passe

Chaque binôme dispose de 3 minutes pour :
1. **Démontrer** ce qui fonctionne (un endpoint, un test, un script)
2. **Identifier** les blocages éventuels (qu'est-ce qui ne marche pas)
3. **Présenter** la feuille de route pour le jour 9 (qu'est-ce qui reste à faire)

#### Le concept de stand-up

Le stand-up est un meeting court et focalisé. Il tire son nom du rugby (le « stand-up » du début de match). Dans le contexte du sprint :
- Il permet à l'intervenant de **comprendre où chacun en est**
- Il permet aux binômes de **sentir qu'ils ne sont pas seuls**
- Il permet de **détecter tôt** les problèmes qui pourraient menacer le deadline

#### Règles d'un bon stand-up

- **3 minutes maximum** par binôme : soyez concis
- **Parlez en termes concrets** : montrez le code ou la commande, ne dites pas juste « ça marche »
- **Soyez honnête sur les blocages** : un blocage documenté est mieux qu'un « tout va bien » qui cache un problème
- **Feuille de route réaliste** : dites ce que vous prévoyez faire pour le jour 9, pas ce que vous souhaiteriez faire

#### Conseil pour le binôme

Préparez votre stand-up à l'avance. Ayez une démonstration courte (30 secondes à 1 minute) prête. Si vous êtes bloqués, dites-le clairement : « Nous sommes bloqués sur X, nous avons besoin d'aide pour Y ».
---

## Concepts clés expliqués simplement

### Le sprint

Un **sprint** est une période de temps fixe (ici, une demi-journée) pendant laquelle une équipe travaille sur un ensemble prédéfini de tâches. Contrairement au travail solo où l'on avance sans structure, le sprint impose :
- Un **objectif clair** : ce qui doit être livré
- Un **temps limité** : ici, de 9h20 à 11h30
- Un **checkpoint** : le stand-up à 11h30 pour faire le point

**Pourquoi c'est utile** : sans sprint, il est facile de perdre de vue l'objectif global au profit de détails techniques. Le sprint force à garder le focus sur la livraison.

### L'autonomie guidée

L'autonomie guidée est une méthode pédagogique où :
- L'étudiant a la **responsabilité** de son travail (il choisit comment procéder)
- L'enseignant est un **guide** disponible en cas de besoin (pas un directeur qui dict chaque étape)

**Équilibre à trouver** : trop d'autonomie → confusion, perte de temps. Trop de guidance → dépendance, manque de confiance. L'objectif est d'atteindre progressivement l'autonomie complète.

### Le stand-up meeting

Le stand-up a trois rôles principaux :
1. **Synchronisation** : chacun sait où les autres en sont
2. **Détection précoce** : un blocage identifié tôt est plus facile à résoudre
3. **Motivation** : voir les autres avancer donne envie d'y aller

**Règle d'or** : un stand-up qui dure plus de 30 minutes pour 4 binômes est trop long. Si quelqu'un parle longtemps, c'est qu'il n'est pas préparé.

### L'intégration continue (et le Code Freeze)

L'**intégration continue** est la pratique de fusionner fréemment le code des développeurs dans une branche commune, en vérifiant à chaque fusion que tout fonctionne.

Le **Code Freeze** est l'étape finale : plus d'ajout de fonctionnalités, seulement des corrections de bugs et de la documentation. C'est le point de non-retour avant la démonstration.

**Pourquoi c'est important** : sans Code Freeze, on a tendance à « améliorer » le projet jusqu'au dernier moment, ce qui risque de casser ce qui marchait. Le Code Freeze protège la version démontrable.

### Le Jalon 8 : Code Freeze et packaging

Le Jalon 8 exige :
- Des **tests automatisés** qui passent
- Un **README** professionnel (démarrage, architecture, installation)
- Un **jeu de démonstration** stable et reproductible
- Un **tag Git** (version) pour marquer l'état final
- Un **support Demo Day** (script de démonstration)
---

## Livrables attendus pour ce jour

À la fin de la journée, chaque binôme doit avoir livré :

### 1. Intégration globale fonctionnelle
- [ ] `docker compose up --build` démarre sans erreur
- [ ] Tous les endpoints du contrat API fonctionnent :
  - `GET /health`
  - `POST /logs`
  - `GET /logs`
  - `GET /logs/{id}`
  - `POST /logs/{id}/analyze`
  - `GET /alerts`
- [ ] La base PostgreSQL persiste les données (redémarrage testé)
- [ ] L'IA fonctionne (avec un fournisseur, même fake)

### 2. Tests et validation
- [ ] Les tests (`pytest`) passent
- [ ] Le projet redémarrable depuis une machine propre
- [ ] Les secrets sont isolés (`.env`, `.gitignore` vérifiés)

### 3. Documentation
- [ ] README mis à jour (démarrage, architecture, endpoints)
- [ ] `.env.example` à jour
- [ ] Jeu de logs de démonstration prêt

### 4. Préparation pour le jour 9
- [ ] Liste des tâches restantes pour le jour 9
- [ ] Blocages identifiés et documentés
- [ ] Plan de code freeze connu

### Ce qui n'est pas attendu ce jour

- **Pas de nouvelles fonctionnalités** : on ne crée pas de nouveaux endpoints
- **Pas de refactorage complet** : on corrige les bugs, on ne réécris pas le code
- **Pas de perfection** : on vise une version démontrable, pas une version production
---

## Erreurs fréquentes et comment les éviter

### ❌ Erreur 1 : Travailler dans le mauvais ordre

**Problème** : Commencer par écrire du code sans d'abord vérifier que l'environnement (Docker, base de données) fonctionne.

**Conséquence** : On passe du temps à écrire du code qui ne peut pas tourner, puis on découvre que le problème est dans la configuration Docker.

**Comment éviter** : 
1. `docker compose up --build` → vérifier que tout démarre
2. `GET /health` → vérifier l'API et la base
3. `POST /logs` → vérifier l'ingestion
4. Progressivement, tester chaque endpoint

**Règle d'or** : faites marcher le plus petit bout du projet avant d'ajouter la complexité.

---

### ❌ Erreur 2 : Ne pas documenter les blocages

**Problème** : Être bloqués sans le noter, ou noter vaguement « problème avec l'IA ».

**Conséquence** : L'intervenant ne peut pas aider efficacement. Vous perdez du temps à expliquer le contexte.

**Comment éviter** :
- Notez exactement quelle commande vous avez exécutée
- Notez le message d'erreur complet (ou la première ligne)
- Notez ce que vous vous attendiez à voir
- Présentez ces informations lors du stand-up

**Exemple de bonne note** :
```
BLOCAGE : POST /logs/1/analyze
Commande : curl -X POST http://localhost:8000/logs/1/analyze
Erreur : 500 Internal Server Error - "NoneType has no attribute 'get'"
Attendu : {"severity":"LOW","category":"INFO",...}
```

---

### ❌ Erreur 3 : Rester isolé au lieu de demander de l'aide

**Problème** : Penser « je vais trouver tout seul », et passer 30 minutes à chercher une erreur évidente.

**Conséquence** : Perte de temps, frustration, et risque de ne pas terminer dans les délais.

**Comment éviter** :
- **Délai maximum** : 10-15 minutes de recherche avant de demander de l'aide
- **Préparez votre question** : avez la commande et le message d'erreur à la main
- **Demandez à l'intervenant ou à un autre binôme** : parfois, un œil extérieur voit ce que vous ne voyez pas

**Rappel** : demander de l'aide n'est pas un échec, c'est une stratégie. Un binôme qui sait demander de l'aide va plus vite qu'un binôme qui refuse de demander.

---

### ❌ Erreur 4 : Mélanger plusieurs problèmes à la fois

**Problème** : Corriger la configuration Docker, le code Python et la base de données en même temps.

**Conséquence** : Impossible de savoir ce qui a résolu le problème. Si cela marche, on ne sait pas pourquoi.

**Comment éviter** :
- **Un problème à la fois** : corrigez un truc, testez, puis passez au suivant
- **Utilisez git** : faites un commit par correction. Ainsi, vous pouvez revenir en arrière si nécessaire.

---

### ❌ Erreur 5 : Négliger les tests

**Problème** : Tester manuellement avec curl, puis oublier de vérifier que les tests automatisés (`pytest`) passent.

**Conséquence** : La démonstration peut échouer car un test qui passait hier ne passe plus aujourd'hui (régression).

**Comment éviter** :
- Exécutez `pytest -q` à la fin de la journée
- Si un test échoue, corrigez-le immédiatement
- Ne laissez pas les tests pour le jour 9

---

### ❌ Erreur 6 : Oublier de vérifier les secrets

**Problème** : Mettre une clé API ou un mot de passe dans le code ou dans un commit Git.

**Conséquence** : Secret exposé dans l'historique Git. Même si vous le supprimez, il reste dans l'historique.

**Comment éviter** :
- `git grep -nE "(api[_-]?key|password|secret)"` avant chaque commit
- Utilisez `.env` et `.env.example`
- Vérifiez `.gitignore` avec `git check-ignore -v .env`

---

### ❌ Erreur 7 : Ne pas prévoir de plan B pour l'IA

**Problème** : La démonstration dépend d'une réponse IA en direct (OpenAI ou Ollama). Si le fournisseur est indisponible, la démonstration échoue.

**Conséquence** : Perte de temps le jour 10, ou démonstration incomplète.

**Comment éviter** :
- Utilisez le **fake provider** par défaut pour la démonstration
- Ayez un jeu de logs et réponses pré-enregistrés
- Testez la démonstration avec le fake provider
---

## Connexions avec les jours suivants

### Vers le Jour 9 (Jeudi 17 septembre) : Testing, documentation & finalisation

Le Jour 8 prépare directement le Jour 9 :
- **Tests** : les tests automatisés écrits et passés aujourd'hui seront améliorés demain
- **Documentation** : le README initié aujourd'hui sera finalisé demain
- **Code Freeze** : on gèle les fonctionnalités aujourd'hui, on les teste et documente demain

**Transition clé** : ce que vous intégrez et testez aujourd'hui (l'assemblage global) est la base sur laquelle vous construisez les tests et la documentation de demain. Si l'intégration n'est pas solide aujourd'hui, les tests de demain seront difficile à écrire.

### Vers le Jour 10 (Vendredi 18 septembre) : Demo Day

Le Jour 8 est le point de départ de la préparation de la démonstration :
- **Jeux de logs** : les logs de démonstration créés aujourd'hui seront utilisés demain
- **Script de démo** : la structure de la démonstration (6 minutes) est pensée aujourd'hui
- **Plan B** : les solutions de secours identifiées aujourd'hui seront affinées demain

**Règle d'or pour la démo** : elle doit raconter un trajet complet : log → ingestion → stockage → analyse → alerte. Chaque étape doit être visible et compréhensible.

### Connexions avec les jours précédents

Le Jour 8 est le aboutissement de :
- **Jour 6** : la persistance PostgreSQL (les données sont stockées)
- **Jour 7** : l'analyse IA (les logs sont analysés)
- **Jour 5** : la sécurisation (les secrets sont isolés, les entrées validées)
- **Jour 3** : la conteneurisation (Docker, Compose)
- **Jour 2** : l'architecture réseau (les scripts, les ports)
- **Jour 1** : Git et collaboration (les branches, les PR)

Tout ce qui a été appris ces jours-là est mis en œuvre aujourd'hui. C'est la preuve que la formation est progressive et cohérente.
---

## Pour aller plus loin

### Conseils pour le travail en équipe

1. **Alternez le pilote et le copilote** : un écrit, l'autre observe et teste. Puisque vous êtes deux, l'un peut tester pendant que l'autre code. Alternez régulièrement pour que chacun reste impliqué.

2. **Communiquez verbalement** : expliquez ce que vous faites à votre partenaire. Ça force à structurer votre pensée et ça permet à l'autre de repérer les erreurs.

3. **Utilisez Git efficacement** : une branche par tâche, un commit par correction. Ne travaillez pas directement sur `main`.

4. **Décidez ensemble** : si vous avez un désaccord sur une approche, discutez-en. Ne laissez pas l'un faire sans l'autre. Le travail d'équipe est une collaboration, pas une compétition.

### Conseils pour la gestion de projet

1. **Planifiez par étapes** : ne dites pas « je vais faire l'API ». Dites : « je vais d'abord vérifier Docker, puis l'endpoint /health, puis POST /logs ».

2. **Testez souvent** : après chaque modification, testez. Ne laissez pas les tests pour la fin.

3. **Documentez les progrès** : tenez un journal de ce qui est fait, ce qui reste, et les blocages. C'est utile pour le stand-up.

4. **Anticipez les dépendances** : si vous avez besoin de la base de données pour tester l'IA, vérifiez d'abord que la base fonctionne.

### Conseils pour la démonstration (Jour 10)

1. **Pratiquez avec le chronomètre** : 6 minutes. Répétez plusieurs fois.

2. **Parlez à tour de rôle** : 50/50 entre les profils. Chacun doit pouvoir expliquer son partie.

3. **Ayez un plan B** : si l'IA ne répond pas, utilisez le fake provider ou un résultat pré-enregistré.

4. **Montrez le trajet complet** : ne montrez pas un endpoint isolé. Montrez un scénario utilisATEUR : on envoie un log, il est stocké, analysé, et on voit l'alerte.

5. **Soyez prêt à répondre aux questions** : 4 minutes de Q&A après la démo. Anticipez les questions : pourquoi ce choix d'architecture ? comment avez-vous sécurisé ? comment testez-vous ?

### Pour aller plus loin (hors du projet)

- **Lire la documentation FastAPI** : https://fastapi.tiangolo.com/
- **Découvrir les bons pratiques DevOps** : https://docs.github.com/en/get-started/quickstart
- **Explorer les outils de monitoring** : Prometheus, Grafana pour aller au-delà des logs
- **Tester d'autres fournisseurs IA** : Anthropic Claude, Google Gemini, modèles open-source
---

## Annexe : Checklist rapide pour le binôme

Utilisez cette checklist pendant le sprint pour vérifier que vous ne rien ne manquez.

### Phase 1 : Démarrage (5 min)
- [ ] `docker compose down` (nettoyer l'ancien)
- [ ] `docker compose up --build` (démarrer proprement)
- [ ] `docker compose ps` (vérifier que les services tournent)

### Phase 2 : Tests de base (10 min)
- [ ] `curl http://localhost:8000/health` → `{"status":"ok"}`
- [ ] `curl -X POST http://localhost:8000/logs -H "Content-Type: application/json" -d '{"message":"test","level":"INFO","source":"demo"}'` → 201
- [ ] `curl http://localhost:8000/logs` → liste les logs

### Phase 3 : Analyse IA (5 min)
- [ ] `curl -X POST http://localhost:8000/logs/1/analyze` → analyse structurée
- [ ] Vérifier la réponse contient : severity, category, summary, recommendations

### Phase 4 : Alertes (3 min)
- [ ] `curl http://localhost:8000/alerts` → liste les alertes (HIGH/CRITICAL)

### Phase 5 : Tests automatisés (5 min)
- [ ] `pytest -q` → tous les tests passent

### Phase 6 : Sécurité (3 min)
- [ ] `git grep -nE "(api[_-]?key|password|secret)" -- . ":(exclude).env.example"` → aucun résultat
- [ ] `git check-ignore -v .env` → .env est bien ignoré

### Phase 7 : Documentation (5 min)
- [ ] README mis à jour
- [ ] `.env.example` à jour
- [ ] Jeu de logs de démonstration prêt

### Phase 8 : Stand-up (5 min)
- [ ] Démonstration prête (30 secondes)
- [ ] Blocages documentés
- [ ] Feuille de route pour le jour 9
