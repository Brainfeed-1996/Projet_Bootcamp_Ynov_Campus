# Guide de S√©curit√©

## Principes de S√©curit√©

### Defense in Depth
Le projet applique plusieurs couches de s√©curit√© :

1. **Network** : Isolation Docker, pare-feu
2. **Application** : Validation, rate limiting, headers de s√©curit√©
3. **Data** : Chiffrement, masquage, hachage
4. **Infrastructure** : Secrets management, scanning

## Configuration S√©curis√©e

### Variables d'environnement sensibles
Les variables sensibles doivent √™tre :
- Stock√©es dans `.env` (ignor√© par Git)
- Ou dans un vault (HashiCorp Vault)
- JAMAIS commit√©es dans le d√©p√¥t

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

## Analyse de S√©curit√©

### Tests de p√©n√©tration
La suite de tests inclut :
- Injection SQL
- XSS
- Mass assignment
- Broken authentication
- Sensitive data exposure

### Scan de d√©pendances
```bash
# V√©rifier les vuln√©rabilit√©s
safety check -r requirements.txt
pip-audit -r requirements.txt
```

### Analyse de code
```bash
# Bandit pour la s√©curit√© Python
bandit -r app.py -f json -o bandit-report.json

# Semgrep pour l'analyse statique
semgrep --config=auto app.py
```

## Bonnes Pratiques

### Pour les d√©veloppeurs
1. Ne jamais commit de secrets
2. Utiliser `git rebase` pour un historique propre
3. √âcrire des tests pour chaque feature
4. Valider avec `pre-commit` avant de push

### Pour l'ops
1. Surveiller les logs d'audit
2. Mettre √† jour les d√©pendances r√©guli√®rement
3. Sauvegarder la base de donn√©es
4. Faire des scans de s√©curit√© r√©guliers

### Pour les auditeurs
1. Consulter le rapport de s√©curit√© (`security_audit.md`)
2. V√©rifier les logs d'acc√®s
3. Auditer les permissions des utilisateurs
4. Contr√¥ler la configuration Vault
## Checklist de DÈploiement

- [ ] Mettre ‡ jour les dÈpendances
- [ ] ExÈcuter les tests de sÈcuritÈ
- [ ] Configurer les variables d'environnement
- [ ] VÈrifier les permissions Vault
- [ ] Sauvegarder la base de donnÈes
- [ ] Surveiller les logs post-dÈploiement

## Headers de SÈcuritÈ

| Header | Valeur | Description |
|--------|--------|-------------|
| X-Content-Type-Options | nosniff | EmpÍche le MIME sniffing |
| X-Frame-Options | DENY | EmpÍche le clickjacking |
| X-XSS-Protection | 1; mode=block | Protection XSS |
| Referrer-Policy | strict-origin-when-cross-origin | Politique de referral |
| Content-Security-Policy | default-src 'self' | Politique CSP |

## Monitoring

### MÈtriques clÈs
- Taux d'erreurs : < 1%
- Latence P99 : < 200ms
- DisponibilitÈ : > 99.9%

### Alertes configurÈes
- Erreurs 500 : ImmÈdiate
- Latence ÈlevÈe : 5 minutes
- Base de donnÈes lente : 2 minutes

## Sauvegarde et Restauration

### Sauvegarde automatique
```bash
pg_dump -h db music_hall > backup.sql
```

### Restauration
```bash
psql -h db music_hall < backup.sql
```

### FrÈquence
- Quotidienne : 3h du matin
- Hebdomadaire : Dimanche 2h
- Mensuelle : Premier du mois

## RÈtention des DonnÈes

| Type de donnÈes | DurÈe de rÈtention |
|-----------------|-------------------|
| Logs | 90 jours |
| Analyses | 90 jours |
| Utilisateurs | 365 jours |
| Logs d'audit | 7 ans |

Les donnÈes sont supprimÈes automatiquement aprËs la pÈriode.
