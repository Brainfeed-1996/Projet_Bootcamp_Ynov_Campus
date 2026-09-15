# Guide de contribution — Log Sentinel API

Ce document décrit les règles communes pour proposer une modification au projet. Toute contribution doit préserver la sécurité, la lisibilité et la capacité à exécuter l'API sans service externe.

## 1. Principes de contribution

- Une contribution doit être petite, relisible et limitée à un objectif.
- Le code et la documentation sont écrits en français lorsque le contexte le permet.
- Les secrets, tokens, clés API, mots de passe et données personnelles ne doivent jamais être commités.
- Les changements de comportement doivent être accompagnés de tests et d'une mise à jour de la documentation concernée.
- Les endpoints publics doivent conserver une validation explicite, des réponses d'erreur stables et une protection contre les injections.
- Les dépendances et les images doivent rester vérifiables par la CI.

## 2. Préparer son environnement

Prérequis :

- Python 3.11 ou supérieur
- Git
- Docker et Docker Compose v2 pour les tests d'intégration
- Les dépendances du projet

Installer les dépendances :

```bash
python -m pip install -r requirements.txt
python -m pip install pre-commit ruff mypy bandit semgrep pip-audit
pre-commit install
```

Pour les tests isolés, utiliser le provider factice et SQLite en mémoire :

```bash
TESTING=1 LLM_PROVIDER=fake pytest -q --disable-warnings
```

## 3. Organisation des branches

Partir d'une branche principale à jour :

```bash
git checkout main
git pull --ff-only
```

Créer une branche descriptive :

```bash
git checkout -b feat/nom-court-de-la-fonctionnalite
git checkout -b fix/nom-court-du-correctif
git checkout -b docs/nom-court-de-la-mise-a-jour
git checkout -b test/nom-court-de-la-couverture
```

Une branche doit porter un seul changement cohérent. Les branches de correction critique peuvent utiliser le préfixe `hotfix/`.

## 4. Standards de code

### Python et FastAPI

- Utiliser Python 3.11+, FastAPI, Pydantic v2 et SQLAlchemy 2.
- Ajouter des annotations de types aux fonctions et aux modèles.
- Respecter une longueur de ligne de 120 caractères, conformément à `pyproject.toml`.
- Nommer les variables et fonctions de façon explicite ; éviter les abréviations ambiguës.
- Centraliser les règles métier dans les modèles Pydantic, les validateurs ou les services dédiés.
- Ne jamais concaténer des valeurs non fiables dans une requête SQL ; utiliser les paramètres SQLAlchemy.
- Gérer explicitement les erreurs attendues et retourner des codes HTTP appropriés.
- Ne pas afficher d'exception brute, de secret ou de donnée sensible dans les réponses et les logs.
- Utiliser des logs structurés avec un `request_id` lorsque le contexte de requête est disponible.
- Conserver le provider factice comme solution de test hors ligne.

### Sécurité

- Valider les types, longueurs, enumérations et formats avant traitement.
- Limiter la taille des payloads, des imports CSV et des opérations bulk.
- Appliquer le rate limiting aux routes sensibles.
- Hacher les mots de passe avec bcrypt et ne jamais stocker de mot de passe clair.
- Utiliser des requêtes paramétrées et des politiques de moindre privilège.
- Redacter les credentials, tokens, adresses email et autres données sensibles avant journalisation.
- Ne pas désactiver un scan ou une règle de sécurité sans justification documentée.

### Documentation

- Mettre à jour le fichier le plus proche du sujet : `README.md`, `SECURITY_GUIDE.md`, `CI_GUIDE.md`, `QUICKREF.md`, `DEMO_DAY.md`, `PITCH.md`, `cours.md` ou `explications.md`.
- Utiliser des titres hiérarchisés, des tableaux pour les options et des blocs de commande copiables.
- Distinguer clairement le comportement actuel, les options de déploiement et la roadmap.
- Indiquer les prérequis, les effets attendus et les étapes de rollback lorsqu'une procédure est opérationnelle.
- Ne pas documenter un endpoint, une variable ou une table comme disponible s'il n'existe pas dans l'implémentation actuelle.

## 5. Tests et checks avant commit

Exécuter les checks dans l'ordre suivant avant de créer une Pull Request :

```bash
# Formatage et lint
ruff check .
ruff format --check .

# Typage
mypy app.py

# Tests hors ligne
TESTING=1 LLM_PROVIDER=fake pytest -q --disable-warnings

# Sécurité
bandit -r app.py -f json -o bandit-report.json --skip B101,B601
semgrep --config=auto app.py
pip-audit -r requirements.txt

# Configuration Docker
docker compose -f compose.yaml config --quiet
docker compose -f compose.yaml -f docker-compose.production.yml config --quiet

# Hooks déclarés par le projet
pre-commit run --all-files
```

Les commandes de scan peuvent nécessiter un environnement CI ou des outils installés séparément. Un avertissement doit être analysé ; il ne doit pas être ignoré silencieusement.

Ajouter des tests pour :

- les chemins de succès et les validations invalides ;
- les limites de taille et de volume ;
- les erreurs de base de données et de provider LLM ;
- les comportements de sécurité et de rate limiting ;
- les régressions liées au changement proposé.

## 6. Conventional Commits

Chaque commit doit utiliser le format :

```text
<type>(<scope>): <description courte>
```

Types courants :

| Type | Usage |
|------|-------|
| `feat` | nouvelle fonctionnalité rétrocompatible |
| `fix` | correction de bug |
| `docs` | documentation |
| `test` | tests |
| `refactor` | refactoring sans changement de comportement |
| `perf` | amélioration de performance |
| `security` | correction ou renforcement de sécurité |
| `chore` | maintenance ou outillage |

Exemples :

```bash
git commit -m "feat(logs): add filtered export endpoint"
git commit -m "fix(auth): reject expired tokens"
git commit -m "docs: document database schema"
git commit -m "test(security): cover CSV injection"
```

Un changement incompatible doit utiliser `!` et inclure une description `BREAKING CHANGE` dans le corps du commit.

## 7. Pull Request

Une Pull Request doit contenir :

- un titre Conventional Commit ;
- une description du problème, de la solution et du comportement attendu ;
- la liste des fichiers et composants concernés ;
- les commandes de test exécutées et leurs résultats ;
- les risques résiduels, migrations ou actions de déploiement ;
- des captures ou exemples lorsqu'un comportement visible change.

Modèle recommandé :

```markdown
## Pourquoi
<problème ou besoin>

## Quoi
<description du changement>

## Comment
<choix de conception et comportement>

## Vérifications
- [ ] `ruff check .`
- [ ] `mypy app.py`
- [ ] `pytest -q --disable-warnings`
- [ ] scans de sécurité
- [ ] validation Compose

## Risques et migration
<risques, migration, rollback>
```

### Revue de code

L'auteur doit :

- relire son diff avant de demander une revue ;
- garder la PR focalisée et éviter les changements de format sans lien avec l'objectif ;
- répondre aux commentaires ou expliquer pourquoi ils ne sont pas appliqués ;
- mettre à jour les tests et la documentation après les changements demandés.

Le relecteur doit vérifier :

- la logique métier et les cas d'erreur ;
- la sécurité, la validation et la gestion des secrets ;
- la couverture de tests ;
- la compatibilité des contrats API et du schéma de données ;
- la lisibilité, les performances et la facilité de rollback.

## 8. Intégration et publication

La CI exécute notamment le lint, le typage, les tests, Bandit, Semgrep, les scans de dépendances et l'image Docker. Une PR ne doit être fusionnée que lorsque les checks obligatoires sont verts ou que leur exception est explicitement approuvée.

Après fusion :

1. vérifier que la branche source peut être supprimée ;
2. suivre la politique de versioning dans `API_CHANGELOG.md` ;
3. créer un tag de version uniquement pour une release validée ;
4. documenter les migrations et le rollback dans le changelog ou le guide associé.

## 9. Définition of Done

Une contribution est terminée lorsque :

- le comportement demandé est implémenté et testé ;
- les checks locaux et la CI sont verts ;
- aucun secret ou artefact temporaire n'est présent dans le diff ;
- la documentation nécessaire est mise à jour ;
- les changements de schéma ou de contrat API sont explicitement décrits ;
- la procédure de déploiement et de retour arrière est connue ;
- la Pull Request a reçu l'approbation requise.
