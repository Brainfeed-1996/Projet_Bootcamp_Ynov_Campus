# Guide de Sécurité

## Principes de Sécurité

### Defense in Depth
Le projet applique plusieurs couches de sécurité :

1. **Network** : Isolation Docker, pare-feu
2. **Application** : Validation, rate limiting, headers de sécurité
3. **Data** : Chiffrement, masquage, hachage
4. **Infrastructure** : Secrets management, scanning

## Configuration Sécurisée

### Variables d'environnement sensibles
Les variables sensibles doivent être :
- Stockées dans `.env` (ignoré par Git)
- Ou dans un vault (HashiCorp Vault)
- JAMAIS commitées dans le dépôt

### Exemple de configuration `.env`
```env
# NE JAMAIS COMMITTER CE FICHIER
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@db:5432/music_hall
OPENAI_API_KEY=sk-your-key-here
```

### Gestion des secrets avec Vault
```bash
# Initialiser Vault
./scripts/vault-init.sh

# Stocker les secrets
vault kv put secret/log-sentinel \
  database_url="postgresql://..." \
  openai_api_key="sk-..." \
  secret_key="..."
```

## Analyse de Sécurité

### Tests de pénétration
La suite de tests inclut :
- Injection SQL
- XSS
- Mass assignment
- Broken authentication
- Sensitive data exposure

### Scan de dépendances
```bash
# Vérifier les vulnérabilités
safety check -r requirements.txt
pip-audit -r requirements.txt
```

### Analyse de code
```bash
# Bandit pour la sécurité Python
bandit -r app.py -f json -o bandit-report.json

# Semgrep pour l'analyse statique
semgrep --config=auto app.py
```

## Bonnes Pratiques

### Pour les développeurs
1. Ne jamais commit de secrets
2. Utiliser `git rebase` pour un historique propre
3. Écrire des tests pour chaque feature
4. Valider avec `pre-commit` avant de push

### Pour l'ops
1. Surveiller les logs d'audit
2. Mettre à jour les dépendances régulièrement
3. Sauvegarder la base de données
4. Faire des scans de sécurité réguliers

### Pour les auditeurs
1. Consulter le rapport de sécurité (`security_audit.md`)
2. Vérifier les logs d'accès
3. Auditer les permissions des utilisateurs
4. Contrôler la configuration Vault