# Configuration CI/CD

## GitHub Actions

Le workflow CI est défini dans `.github/workflows/ci.yml`. Il exécute :

1. **Test des dépendances** : Vérification de `requirements.txt`
2. **Linting** : Analyse du code avec `ruff`
3. **Type checking** : Vérification des types avec `mypy`
4. **Tests** : Exécution de la suite de tests avec `pytest`
5. **Sécurité** : Scan avec `trivy` (optionnel)

## Déclencheurs

- **Push** sur `main` et `develop`
- **Pull Request** sur `main`
- **Tags** de version (`v*`)

## Variables d'environnement CI

| Variable | Description | Requis |
|----------|-------------|--------|
| DOCKER_USERNAME | Utilisateur Docker Hub | Oui |
| DOCKER_TOKEN | Token d'accès Docker Hub | Oui |
| OPENAI_API_KEY | Clé API OpenAI (pour tests) | Non |
| PYPI_TOKEN | Token PyPI pour publication | Non |

## Workflows

### Tests unitaires
```yaml
- name: Run tests
  run: pytest tests/ -v --cov=app --cov-report=xml
```

### Build et Push Docker
```yaml
- name: Build and push
  uses: docker/build-push-action@v5
  with:
    push: ${{ github.event_name == 'push' }}
    tags: ${{ steps.meta.outputs.tags }}
```

### Publication sur PyPI
```yaml
- name: Publish
  if: startsWith(github.ref, 'refs/tags/v')
  run: |
    python -m build
    twine upload dist/*
```

## Quality Gates

### Couverture minimale
- Couverture des tests : > 80%
- Tests de sécurité : 100% des endpoints couverts
- Linting : 0 erreurs critiques

### Analyse de sécurité
- Trivy scan pour les images Docker
- Bandit pour l'analyse de code Python
- Safety pour les dépendances

---

## Pipeline de Déploiement

### Environnements
- **Development** : Branche `develop`, déploiement automatique
- **Staging** : Branche `staging`, tests manuels requis
- **Production** : Branche `main`, validation manuelle requise

### Procédures de déploiement
1. Merge vers `main` après review
2. Tag de version (`v1.2.0`)
3. Workflow de build et push Docker
4. Déploiement sur l'infrastructure de production
5. Vérification de santé post-déploiement

### Rollback
```bash
# Arrêter le conteneur actuel
docker stop app-prod

# Redémarrer la version précédente
docker run -d --name app-prod-backup \
  -e DATABASE_URL=$DATABASE_URL \
  olivier-robert-duboille/log-sentinel:v1.1.0
```

## Monitoring

### Métriques exposées
- `/metrics` : Métriques Prometheus
- `/health` : Santé de l'application
- `/health/detailed` : Santé détaillée (base de données, providers)

### Logs structurés
```json
{
  "timestamp": "2025-09-18T10:30:00Z",
  "level": "INFO",
  "message": "Log created",
  "log_id": 42,
  "duration_ms": 15
}
```

### Alertes configurées
- Taux d'erreurs > 5% pendant 5 minutes
- Latence P99 > 500ms pendant 2 minutes
- Base de données indisponible