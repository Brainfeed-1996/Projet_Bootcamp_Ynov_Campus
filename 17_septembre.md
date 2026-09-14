# Jour 9 — Jeudi 17 septembre : Testing, Documentation & Finalisation

## Des logs bruts à une alerte exploitable

> **Semaine 2 — Data, IA et livrables du projet**
> 09h00–12h00 · Fil rouge Jalon 8 : Code Freeze et packaging

---

## 1. Résumé exécutif du jour

Ce jour est le **point d'orgue de la semaine 2**. Pendant trois blocs matinaux, vous passerez de code en cours de développement à un projet **stable, testé, documenté et prêt à être démontré**. L'objectif n'est plus d'ajouter des fonctionnalités : c'est de **geler ce qui existe**, s'assurer qu'il fonctionne de manière fiable, et préparer la démonstration finale de demain.

Concrètement, la journée se découpe en quatre phases :

1. **Qualité, packaging & tests** (09h00–09h40) — Poser les fondations d'un projet professionnel : README, tests automatisés, linting.
2. **Qualification du code** (09h40–10h30) — Écrire un test unitaire, faire passer le linter, et corriger ce qui ne passe pas.
3. **Fil rouge · Jalon 8** (10h30–11h30) — Geler les fonctionnalités, finaliser la documentation, préparer le support Demo Day.
4. **Répétition générale** (11h30–12h00) — Vérifier les démonstrations et préparer des solutions de secours.

> 🎯 **En une phrase** : aujourd'hui, on transforme un projet qui *fonctionne* en un projet qui *démontre*.

---

## 2. Objectifs pédagogiques

À l'issue de cette journée, chaque binôme sera capable de :

- **Rédiger un README professionnel** contenant démarrage, architecture et installation.
- **Définir et exécuter des tests automatisés** avec pytest dans le contexte d'une API FastAPI.
- **Utiliser un linter** (Ruff) pour détecter et corriger les anomalies de style et de qualité.
- **Comprendre et appliquer le concept de Code Freeze** : ce qu'on gèle, pourquoi, et comment.
- **Préparer un jeu de démonstration** reproductible et un plan de secours.
- **Réaliser une répétition générale** chronométrée pour valider la faisabilité de la démo.

---

## 3. Détaillement horaire de chaque activité

### 3.1 — Qualité, packaging & tests (09h00–09h40) · 40 min

> *« On ne peut pas tester ce qu'on ne peut pas installer. »*

#### Ce qu'on fait

**a) Construire un README professionnel**

Le README est la **carte de visite** de votre projet. Un juré ou un nouveau développeur doit pouvoir :

1. Cloner le dépôt.
2. Lancer l'application en un maximum de commandes.
3. Comprendre l'architecture en une lu.

Un README minimum viable contient :

- **Titre et description** : une phrase qui résume le projet.
- **Prérequis** : ce qui doit être installé (Python 3.11+, Docker, Git).
- **Installation** : les commandes exactes, du clone au premier lancement.
- **Démarrage rapide** : 3 à 5 commandes pour avoir l'API qui répond.
- **Architecture** : un schéma ou une description des composants (API, PostgreSQL, fournisseur IA).
- **Tests** : comment lancer la suite de tests.
- **Endpoints** : les routes principales avec un exemple.
- **Sécurité** : comment les secrets sont gérés.
- **Problèmes courants et solutions** : un tableau de dépannage.

> 💡 **Conseil** : rédigez le README comme si vous le lisiez sur une machine complètement neuve, sans aucune mémoire du projet.

**b) Découvrir les tests automatisés avec pytest**

Un **test automatisé** est un petit programme qui vérifie un comportement attendu de votre application, sans intervention humaine. Pytest est l'outil standard en Python.

Pourquoi c'est indispensable dans ce projet :

- Vous avez un **fournisseur IA pluggable** (OpenAI, Ollama, Fake). Les tests doivent vérifier le comportement sans dépendre d'un vrai service externe.
- Vous avez des **rôles utilisateurs** (admin, writer, reader). Les tests doivent confirmer que chaque rôle obtient exactement les droits prévus.
- Vous allez **geler le code** ce soir : les tests sont votre filet de sécurité. Si quelque chose casse après une modification, les tests le diront immédiatement — c'est une **régression**.

Concept clé : le **faux fournisseur** (FakeProvider). Dans vos tests, vous ne faites jamais appel à OpenAI ou Ollama. Vous utilisez un fournisseur factice qui retourne des résultats déterministes et rapides. Cela rend les tests :

- **Rapides** : aucune latence réseau.
- **Déterministes** : le même entrée donne toujours la même sortie.
- **Indépendants** : pas de clé API, pas de quota, pas de réseau requis.

**c) Découvrir les outils de linting**

Le **linting** est l'analyse automatique de votre code pour détecter :

- Des erreurs de style (noms de variables incohérents, indentation).
- Des bugs potentiels (variables non utilisées, imports manquants).
- Des problèmes de maintenabilité (fonctions trop longues, complexité excessive).

Dans ce projet, le linter configuré est **Ruff** (via `pyproject.toml`). Il combine les règles de style (formatage) et les règles de qualité (détection de bugs).

```toml
# pyproject.toml — Configuration de Ruff
[tool.ruff]
line-length = 120

[tool.ruff.lint]
select = ["I001", "F401"]
ignore = ["B008"]
```

- `I001` : imports ordonnés (isort).
- `F401` : import non utilisé (flake8).
- `B008` : ignoré (certains patterns de décorateurs légitimes).

> 📦 **Connexion outil** : `pytest` pour les tests, `ruff` pour le linting, `git` pour la version. Ces trois outils forment la **trinité qualité** d'un projet professionnel.

---

### 3.2 — Qualification du code (09h40–10h30) · 50 min

> *« Un code qui n'a pas été testé n'est pas un code terminé. »*

#### Ce qu'on fait

**a) Écrire un test unitaire simple**

Un **test unitaire** vérifie le comportement d'une unité de code isolée — typiquement une fonction ou une route.

Exemple concret dans le contexte de l'API :

```python
def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "database": "up"}
```

Ce test vérifie que :

1. L'endpoint `/health` répond avec le code HTTP 200.
2. Le corps de la réponse contient exactement `{"status": "ok", "database": "up"}`.

Pour l'écrire, vous avez besoin de :

- **Un client de test** : `TestClient` de FastAPI, qui simule des requêtes HTTP sans lancer de serveur.
- **Une base de données de test** : souvent une base SQLite en mémoire activée par la variable d'environnement `TESTING=1`.
- **Des données de fixture** : les utilisateurs admin/writer/reader sont créés avant chaque test via une fonction `_bootstrap_all()`.

Les tests couvrent dans ce projet :

| Catégorie | Exemples |
|-----------|----------|
| **Santé** | `/health` répond correctement |
| **Authentification** | Login success, mauvais mot de passe, utilisateur inexistant |
| **Utilisateurs** | Création admin-only, forbidden pour writer/reader, validation des champs |
| **Logs** | Création, filtrage par level/source/limit, validation des données |
| **Analyses** | Analyse avec FakeProvider, provider défaillant, réponse IA invalide |
| **Alertes** | Filtrage HIGH/CRITICAL, limites, invalidité des paramètres |
| **Sécurité** | Headers de sécurité, CORS, sanitization des données |

**b) Nettoyer le code avec le linter**

Lancez Ruff sur l'ensemble du code source :

```bash
ruff check .
```

Pour chaque anomalie signalée :

1. **Lisez le message** : Ruff indique le fichier, la ligne, la règle violée et une description.
2. **Corrigez** : supprimez l'import inutilisé, renommez la variable, reformatez le bloc.
3. **Répétez** jusqu'à ce que `ruff check .` ne retourne aucune erreur.

Pour le formatage automatique :

```bash
ruff check --fix .
```

> ⚠️ **Attention** : le fix automatique ne résout pas tout. Certaines corrections demandent une réflexion sur la logique du code. Relisez toujours les modifications proposées avant de les accepter.

**c) Faire passer les tests**

```bash
pytest -v
```

L'option `-v` (verbose) affiche chaque test individuellement. Vous devez voir **tous les tests passer** (ok en vert). Si un test échoue :

1. Lisez le message d'erreur : il indique quelle assertion a échoué et pourquoi.
2. Vérifiez si c'est une régression (le test passait avant et plus maintenant).
3. Corrigez le code ou le test selon le diagnostic.
4. Relancez `pytest -v` jusqu'à ce que tout soit vert.

> 🔴 **Règle d'or** : un code qui n'est pas testé n'est pas du code. Un code dont les tests échouent n'est pas du code prêt pour la démo.

---

### 3.3 — Fil rouge · Jalon 8 : Code Freeze et packaging (10h30–11h30) · 60 min

> *« Le Code Freeze, ce n'est pas l'arrêt du développement. C'est l'arrêt de l'ajout de nouveautés. »*

#### Ce qu'on fait

**a) Geler les fonctionnalités**

Le **Code Freeze** est le moment où vous cessez d'ajouter des fonctionnalités pour vous concentrer sur la stabilité. À partir de ce point :

- **Pas de nouvelle route** : les endpoints existants sont figés.
- **Pas de changement d'architecture** : on ne réécrit pas un module pour le « plaire ».
- **Pas de nouvelle dépendance** : on n'ajoute pas de bibliothèque qui risque de casser quelque chose.
- **Seules les corrections de bugs** sont autorisées, et elles doivent être **re-testées immédiatement**.

Pour appliquer le Code Freeze :

1. Faites une liste des fonctionnalités à montrer (le « jeu de démonstration »).
2. Vérifiez que chacune fonctionne avec un scénario complet.
3. Écartez tout le reste. Ce qui n'est pas dans la liste ne sera pas dans la démo.

#### Vocabulaire clé du Jalon 8

| Terme | Définition simple | Exemple dans le projet |
|-------|-------------------|------------------------|
| **Régression** | Un comportement qui fonctionnait avant mais qui est cassé par une modification | Vous corrigez un bug de filtrage et soudain la création de log échoue |
| **Test automatisé** | Un programme qui vérifie un résultat attendu sans intervention humaine | `pytest -v` lance 16 tests en 2 secondes |
| **Version** | Un état identifié du projet auquel on peut revenir | `v1.0-demo` : l'état figé pour la démonstration |
| **Tag Git** | Une étiquette posée sur un commit précis pour marquer une version importante | `git tag -a v1.0-demo -m "Demo Day"` |
| **Plan B** | Une solution de secours préparée pour poursuivre si une dépendance échoue | `LLM_PROVIDER=fake` si OpenAI est indisponible |

**b) Finaliser la documentation**

La documentation finale doit inclure :

- **README** : mis à jour avec les commandes de démarrage, la liste des endpoints, et la procédure de test.
- **DEMO_DAY.md** : le support de démonstration (timing, commandes, plans de secours).
- **DEMO_SCRIPT.md** : les commandes exactes à copier-coller pour la démo.
- **CI_GUIDE.md** : explication du pipeline CI/CD et de la qualité.
- **PITCH.md** : le pitch du projet en quelques paragraphes.

> 💡 **Conseil** : chaque document doit pouvoir être lu indépendamment. Un membre du binôme doit pouvoir expliquer un aspect du projet sans lire les autres documents.

**c) Préparer le support Demo Day**

Le support Demo Day comprend :

1. **Un jeu de démonstration** : un ensemble de commandes `curl` pré-testées qui montrent un scénario utilisateur complet (créer un log → analyser → filtrer → vérifier les alertes).
2. **Un timing minute par minute** : qui parle quand, pendant combien de temps, quel support (terminal, slide, code) à chaque instant.
3. **Des plans de secours** : que faire si Docker ne démarre pas, si l'IA est indisponible, si un endpoint échoue.
4. **Une répartition 50/50** : le temps de parole est partagé équitablement entre les deux membres du binôme.

Exemple de plan de secours pour l'IA :

| Scénario | Déclencheur | Action | Message au jury |
|----------|-------------|--------|-----------------|
| LLM indisponible | `/analyze` → 502 ou timeout | Basculez `LLM_PROVIDER=fake` | « Le fallback fake garantit la démo et la résilience en production. » |

---

### 3.4 — Répétition générale (11h30–12h00) · 30 min

> *« On ne démontre pas ce qu'on n'a pas répété. »*

#### Ce qu'on fait

**a) Vérifier les démonstrations**

1. Lancez l'application complète : `docker compose up --build -d`.
2. Exécutez chaque commande du jeu de démonstration dans l'ordre.
3. Vérifiez que chaque réponse est correcte et dans les temps.
4. Chronométrez-vous : la démo doit tenir en **6 minutes maximum**.

**b) Préparer des solutions de secours**

Testez chaque scénario de secours :

- **Si Docker échoue** : avez-vous un mode local ? (`TESTING=1 LLM_PROVIDER=fake uvicorn app:app`)
- **Si l'IA est down** : avez-vous vérifié que `fake` fonctionne ?
- **Si un endpoint échoue** : avez-vous une commande alternative ?
- **Si un membre est absent** : l'autre membre peut-il faire toute la démo seul ?

**c) Valider la répartition 50/50**

Chaque membre doit savoir :

- Quelles commandes il va exécuter.
- Quelles phrases il va prononcer.
- Quand il prend la parole et quand il passe le relais.

> ⚠️ **Piège** : ne pas répéter en condition réelle. Un binôme qui répète chronométré découvre ses points faibles *avant* la démo, pas pendant.

---

## 4. Concepts clés expliqués simplement

### 4.1 — Tests automatisés

Un test automatisé est un **programme qui vérifie** qu'un bout de votre application se comporte comme prévu, sans qu'un humain doive cliquer ou lire des écrans.

Dans le contexte de Log Sentinel API :

```python
def test_create_log_success():
    # 1. Préparer les données (un token d'authentification)
    _, writer_token, _ = _bootstrap_all()

    # 2. Envoyer une requête (créer un log)
    resp = client.post("/logs", json={
        "message": "Connection timeout",
        "level": "ERROR",
        "source": "api"
    }, headers=_auth_header(writer_token))

    # 3. Vérifier le résultat
    assert resp.status_code == 201          # La création a réussi
    assert resp.json()["message"] == "Connection timeout"  # Le message est conservé
    assert resp.json()["level"] == "ERROR"   # Le niveau est correct
```

Les trois phases de tout test :

1. **Arrange** (préparer) : créer les données nécessaires.
2. **Act** (agir) : exécuter l'action à tester.
3. **Assert** (vérifier) : confirmer que le résultat est attendu.

### 4.2 — pytest

**pytest** est le framework de tests pour Python. Il découvre automatiquement les fonctions dont le nom commence par `test_`, les exécute et rapporte les résultats.

Commandes essentielles :

| Commande | Ce qu'elle fait |
|----------|-----------------|
| `pytest` | Lance tous les tests |
| `pytest -v` | Affiche chaque test individuellement (verbose) |
| `pytest -q` | Mode silencieux (uniquement le résumé) |
| `pytest -x` | S'arrête au premier échec |
| `pytest test_app.py::test_health` | Lance un seul test |

Dans ce projet, les tests utilisent :

- `TestClient` de FastAPI pour simuler des requêtes HTTP.
- SQLite en mémoire (`TESTING=1`) comme base de données de test.
- Un `FakeLLMProvider` pour simuler l'analyse IA sans réseau.

### 4.3 — Linting

Le **linting** est l'inspection automatique du code source pour y détecter des problèmes de **style**, de **qualité** ou de **correction**.

Imaginez un correcteur orthographique, mais pour votre code :

- **Style** : « Vous avez oublié un espace après la virgule. »
- **Qualité** : « Cette variable est définie mais jamais utilisée. »
- **Correction** : « Cette importation est inutile, elle peut supprimer. »

Outil utilisé dans ce projet : **Ruff** (très rapide, écrit en Rust).

```bash
# Vérifier le code
ruff check .

# Corriger automatiquement ce qui est possible
ruff check --fix .

# Formater le code automatiquement
ruff format .
```

### 4.4 — README

Le **README** est le fichier principal de documentation d'un projet. C'est la première chose qu'un visiteur lit.

Structure recommandée :

```
# Log Sentinel API

Description courte (1-2 phrases).

## Installation
3-5 commandes pour démarrer.

## Démarrage rapide
Le chemin le plus court vers "ça marche".

## Architecture
Schéma ou description des composants.

## Endpoints
Table ou liste des routes principales.

## Tests
Comment lancer et interpréter les tests.

## Sécurité
Gestion des secrets, hardening.

## Problèmes courants
Tableau de dépannage.
```

### 4.5 — Code Freeze

Le **Code Freeze** est une période pendant laquelle on **arrête d'ajouter de nouvelles fonctionnalités** pour se concentrer sur la stabilité et la qualité.

Ce n'est pas un arrêt de travail. C'est un changement de priorité :

- **Avant** le freeze : on code, on innove, on construit.
- **Pendant** le freeze : on teste, on documente, on répare, on répète.

Le freeze est lié à une **version**. Quand tout est prêt, on crée un **tag Git** pour marquer cet état :

```bash
git tag -a v1.0-demo -m "Demo Day — version de démonstration"
git push origin v1.0-demo
```

Ce tag permet de revenir à cet état exact à tout moment, même si le code a évolué entre-temps.

### 4.6 — Plan B

Le **Plan B** est la solution de secours préparée à l'avance pour chaque scénario d'échec.

Principe fondamental : **une démo ne doit jamais s'arrêter**. Si une dépendance échoue, il faut avoir un moyen de continuer.

Plans B de ce projet :

| Défaillance | Plan B |
|-------------|--------|
| OpenAI/Ollama injoignable | `LLM_PROVIDER=fake` — déterministe, offline |
| PostgreSQL down | SQLite en mémoire via `TESTING=1` |
| Docker indisponible | Démarrage direct avec `uvicorn` en local |
| Port 5000 occupé | Changer le port dans `compose.yaml` |
| Membre absent | L'autre reprend la totalité de la démo |

---

## 5. Livrables attendus

À la fin de cette journée, le binôme doit avoir produit :

| # | Livrable | Description | Critère de qualité |
|---|----------|-------------|-------------------|
| 1 | **Tests automatisés** | Suite `pytest` complète et verte | Tous les tests passent en moins de 5 secondes |
| 2 | **README final** | Professionnel, complet et testé | Un inconnu peut démarrer le projet en le lisant |
| 3 | **Jeu de démonstration** | Commandes `curl` pré-testées | Chaque commande produit le résultat attendu |
| 4 | **Tag de version** | Tag Git sur le commit final | `git tag` affiche `v1.0-demo` (ou équivalent) |
| 5 | **Support Demo Day** | Document avec timing, plans de secours, répartition 50/50 | La démo tient en 6 minutes chrono |
| 6 | **Code linté** | Aucune erreur Ruff | `ruff check .` ne retourne rien |
| 7 | **Linting configuré** | `pyproject.toml` avec la configuration Ruff | Le fichier existe et est cohérent |

> ✅ **Definition of Done du Jalon 8** : Le projet repart sur une machine propre (`git clone` → installation → démarrage en 1 commande), les tests passent sans accès à une vraie IA, la démonstration tient en 6 minutes avec répartition 50/50.

---

## 6. Erreurs fréquentes et comment les éviter

### 🔴 Erreur 1 : Modifier le cœur du projet juste avant la démonstration sans rejouer les tests

**Pourquoi c'est un problème** : une modification de dernière minute peut casser un fonctionnement qui marchait. Vous ne la découvrirez qu'en situation de stress, devant le jury.

**Comment l'éviter** :

- Appliquez le Code Freeze strictement : aucune nouvelle fonctionnalité après 10h30.
- Si vous trouvez un bug, corrigez-le, puis **rejouez immédiatement tous les tests** avant de continuer.
- Demandez-vous : « Est-ce que cette modification rend la démo plus fiable ou plus claire ? » Si la réponse est non, ne la faites pas.

---

### 🔴 Erreur 2 : Dépendre d'une réponse IA en live sans prévoir de secours

**Pourquoi c'est un problème** : OpenAI ou Ollama peuvent être lents, indisponibles, ou produire une réponse inattendue pendant la démo. Vous pouvez perdre 30 secondes à attendre, puis échouer.

**Comment l'éviter** :

- Gardez `LLM_PROVIDER=fake` comme valeur par défaut. Le faux fournisseur est toujours disponible, toujours rapide, toujours correct.
- Mentionnez explicitement au jury que le fallback existe : « L'IA est un service externe ; le fallback garantit la démo et la résilience en production. »
- Testez le basculement entre providers avant la démo.

---

### 🔴 Erreur 3 : Présenter le code écran par écran au lieu de montrer un scénario utilisateur complet

**Pourquoi c'est un problème** : montrer du code est ennuyeux et difficile à suivre. Le jury veut voir un **trajet utilisateur** : « l'utilisateur fait ceci, le système répond cela ».

**Comment l'éviter** :

- Préparez un **scénario narratif** : « Un administrateur reçoit une alerte de sécurité dans ses logs. Il crée un log d'erreur, demande une analyse IA, et le système génère une alerte HIGH. »
- Utilisez des **commandes curl** dans le terminal plutôt que de naviguer dans le code source.
- Chaque démonstration doit durer **10 à 15 secondes maximum** par écran de code.

---

### 🔴 Erreur 4 : Ne pas chronométrer la répétition

**Pourquoi c'est un problème** : une démo qui dépasse le temps imparti est pénalisée, même si elle est excellente.

**Comment l'éviter** :

- Chronométrez chaque répétition avec un téléphone ou un chronomètre visible.
- Coupez le contenu qui dépasse. Mieux vaut un scénario complet de 5 minutes qu'un scénario incomplete de 7 minutes.

---

### 🔴 Erreur 5 : Préparer la démo uniquement sur la machine du binôme

**Pourquoi c'est un problème** : si la machine de démo est différente (problème technique, panne, oubli de clé USB), vous n'avez rien.

**Comment l'éviter** :

- Votre projet doit démarrer de manière **reproductible** sur n'importe quelle machine (`git clone` → `./scripts/init-docker-secrets.sh` → `docker compose up`).
- Ayez un **mode fallback** qui ne nécessite ni Docker ni IA (voir Section 4.6).
- Testez sur au moins deux machines différentes avant la démo.

---

### 🔴 Erreur 6 : Mélanger les rôles dans la démo

**Pourquoi c'est un problème** : si un seul membre parle pendant toute la démo, l'autre est invisible et l'évaluation 50/50 échoue.

**Comment l'éviter** :

- Rédigez un **tableau de répartition** précis : qui parle à quelle minute.
- Répétez ensemble pour vérifier que les transitions sont fluides.
- Utilisez un signal discret pour indiquer le changement d'orateur (un regard, une note dans le coin de l'écran).

---

## 7. Connexions avec le jour suivant (Demo Day — Vendredi 18 septembre)

Ce jour pose les **fondations directes** de la démonstration finale de demain. Voici comment chaque activité d'aujourd'hui alimente la soutenance de demain :

| Activité du Jour 9 | Utilisation le Jour 10 |
|---------------------|------------------------|
| **README finalisé** | Le jury peut consulter la documentation si besoin. Le README est aussi une preuve de votre rigueur. |
| **Tests qui passent** | Vous avez la certitude que chaque endpoint fonctionne. Plus de surprise en démo. |
| **Jeu de démonstration** | Les commandes `curl` préparées sont copiées dans `demo-commands.sh` et utilisées en direct. |
| **Tag Git posé** | Vous pouvez revenir à l'état stable si la démo dérape. Le tag est votre filet de sécurité. |
| **Support Demo Day** | Le timing minute par minute est suivi pendant la soutenance. Le Plan B est lu à haute voix si un problème survient. |
| **Répétition chronométrée** | La répétition d'aujourd'hui détermine ce que vous gardez et ce que vous coupez demain. |
| **Code linté** | Un code propre inspire confiance. Si le jury demande à voir le code, il voit un code organisé. |

> 🔗 **Fil conducteur** : La semaine 2 a progressé de la donnée (PostgreSQL, jour 6) à l'IA (jour 7), puis à la qualité (jours 8-9). Demain, tout converge dans la **restitution**.

**Soirée du Jour 9 — Préparation pour le Jour 10** :

1. Vérifiez que `docker compose up --build -d` fonctionne depuis zéro.
2. Vérifiez que `pytest -v` passe entièrement.
3. Relancez le jeu de démonstration en entier, chronométré.
4. Relisez le support Demo Day pour confirmer les horaires et les rôles.
5. Dormez. Un cerveau reposant présente mieux qu'un cerveau fatigué qui a tout relu une dernière fois.

---

## 8. Pour aller plus loin — Conseils pratiques

### Conseil 1 : Adoptez la mentalité « D'où viendrai-je ? »

Avant chaque modification, posez-vous la question : « Si cette modification casse quelque chose, comment vais-je le savoir ? ». Si la réponse est « je le verrai en démo », la modification est risquée. Si la réponse est « les tests le diront », la modification est safe.

### Conseil 2 : Utilisez les branches Git intelligemment

Ne travaillez pas directement sur `main`. Créez une branche par intention :

```bash
git switch -c fix/health-endpoint
# ... corrections ...
git add .
git commit -m "fix: health endpoint retourne status ok"
git push origin fix/health-endpoint
# Ouvrir une Pull Request, relire, fusionner
```

Le jour J, vous fusionnez tout dans `main` et créez le tag.

### Conseil 3 : Documentez vos décisions, pas juste vos fonctionnalités

Dans le README et le support Demo Day, expliquez **pourquoi** vous avez fait certains choix :

- « Nous utilisons `FakeProvider` dans les tests pour éviter les dépendances réseau. »
- « Nous avons choisi SQLite en mémoire pour les tests car il ne nécessite pas de service externe. »
- « Le Plan B repose sur `LLM_PROVIDER=fake` car il est déterministe et rapide. »

### Conseil 4 : Préparez des phrases clés, pas des réponses détaillées

Quand le jury pose une question pendant la démo, vous n'avez pas besoin d'une réponse exhaustive. Préparez **3 à 5 phrases clés** :

1. « Nous avons choisi X parce que Y. »
2. « La contrainte principale était Z, donc nous avons opté pour W. »
3. « Ce choix a un impact sur la production car T. »

Si la question dépasse votre préparation, dites honnêtement : « C'est un bon point. En production, nous étudierions cela avec [approche]. Pour la démo, le choix actuel est [justification courte]. »

### Conseil 5 : Le timing de la démo est la compétence la plus importante

Une démo technique parfaite qui dure 7 minutes au lieu de 6 est pénalisée. Entraînez-vous à :

- **Couper** les explications qui ne servent pas le scénario.
- **Raccourcir** les transitions (« Passons à... » au lieu d'une longue introduction).
- **Sauter** une étape si le temps presse (mais gardez le scénario complet).

### Conseil 6 : Utilisez la commande `git stash` pour basculer rapidement

Si vous devez tester quelque chose sans risquer votre code stable :

```bash
git stash          # Sauvegarde vos modifications en attente
# ... tests rapides ...
git stash pop      # Retrouve vos modifications
```

### Conseil 7 : Vérifiez votre `.gitignore` avant de créer le tag final

```bash
git status         # Vérifiez ce qui sera commité
git grep -nE "(api[_-]?key|password|secret)" -- . ":(exclude).env.example"
```

Aucun secret ne doit apparaître dans le dépôt avant de taguer.

### Conseil 8 : La démo raconte une histoire

La meilleure démo n'est pas une liste de features. C'est un **scénario utilisateur** qui a un début, un milieu et une fin :

1. **Début** : « Un administrateur ouvre l'application et voit que la santé est OK. »
2. **Milieu** : « Il crée un log d'erreur, demande une analyse, et le système détecte un problème. »
3. **Fin** : « Il consulte les alertes filtrées et prend une décision. »

Chaque étape doit répondre à une question simple : **qu'envoie-t-on, où va la donnée, comment vérifie-t-on le résultat ?**

---

## Annexes

### A — Commandes essentielles du Jour 9

```bash
# Lancer les tests
pytest -v

# Lancer les tests en mode rapide (arrêt au premier échec)
pytest -x -q

# Lancer un seul test
pytest test_app.py::test_health -v

# Lancer le linter
ruff check .

# Corriger automatiquement
ruff check --fix .

# Formater le code
ruff format .

# Vérifier que Docker est healthy
docker compose ps

# Tester la santé de l'API
curl http://localhost:5000/health

# Créer un tag de version
git tag -a v1.0-demo -m "Demo Day"
git push origin v1.0-demo

# Vérifier les secrets dans le dépôt
git grep -nE "(api[_-]?key|password|secret)" -- .
```

### B — Checklist pré-Demo Day (soir du Jour 9)

- [ ] `git clone` sur une machine propre → `./scripts/init-docker-secrets.sh` → `docker compose up --build -d` : tout vert
- [ ] `curl http://localhost:5000/health` → `{"status":"ok","database":"up"}`
- [ ] `pytest -v` : tous les tests passent
- [ ] `ruff check .` : aucune erreur
- [ ] Jeu de démonstration testé en entier, chronométré
- [ ] Support Demo Day relu par les deux membres
- [ ] Plans de secours testés (mode fake, mode local)
- [ ] Tag Git posé et poussé
- [ ] Répartition 50/50 confirmée et répétée
- [ ] Aucun secret dans le dépôt (`git grep` négatif)

### C — Récapitulatif de la Semaine 2

| Jour | Date | Thème | Jalon |
|------|------|-------|-------|
| J06 | Lundi 14 | PostgreSQL & persistance | Jalon 6 |
| J07 | Mardi 15 | IA & APIs REST | Jalon 7 |
| **J08** | **Mercredi 16** | **Sprint de développement** | **Intégration globale** |
| **J09** | **Jeudi 17** | **Testing, documentation & finalisation** | **Jalon 8 — Code Freeze** |
| J10 | Vendredi 18 | Restitution & Demo Day | **Démo finale** |

---

*Document pédagogique — Jour 9 du projet « Des logs bruts à une alerte exploitable»  
Semaine 2 · Semaine 2 « Data, IA et livrables du projet»  
Ynov Bootcamp DevSecOps — Défensive*
