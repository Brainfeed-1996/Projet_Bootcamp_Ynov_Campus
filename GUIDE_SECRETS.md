# Guide d'utilisation - Scan de vulnérabilités et gestion des secrets

## Scan de vulnérabilités (Trivy)

### Dans le CI (GitHub Actions)

Le workflow CI (.github/workflows/ci.yml) exécute automatiquement :
1. **Trivy** pour l'analyse de l'image Docker
2. **Upload des résultats** vers GitHub Security

**Configuration requise :**
- Les vulnérabilités HIGH/CRITICAL déclenchent un échec du workflow
- Trivy est exécuté lors du build via le stage `trivy-scanner`

### Localement avec Trivy

```bash
# Scanner l'image
trivy image music-hall:latest

# Scanner le système de fichiers
trivy fs --severity HIGH,CRITICAL .
```

## Gestion des secrets

### Option 1 : Docker Secrets (recommandé pour le développement)

1. **Initialiser les secrets :**
```bash
chmod +x scripts/init-docker-secrets.sh
./scripts/init-docker-secrets.sh
```

2. **Démarrer en développement :**
```bash
docker compose up -d
```

### Option 2 : Production avec Docker Secrets

1. **Initialiser les secrets :**
```bash
./scripts/init-docker-secrets.sh
```

2. **Démarrer en production :**
```bash
docker compose -f compose.yaml -f docker-compose.production.yml up -d
```

### Option 3 : HashiCorp Vault (production avancée)

1. **Démarrer Vault :**
```bash
docker compose -f compose.yaml -f docker-compose.vault.yml up -d
```

2. **Initialiser les secrets dans Vault :**
```bash
export VAULT_TOKEN=s.test
./scripts/vault-init.sh
```

3. **Récupérer les secrets au runtime** via Vault Agent

## Bonnes pratiques

- Les secrets ne doivent jamais être commit dans le dépôt
- Utiliser `.gitignore` pour exclure les répertoires de secrets
- Changer tous les mots de passe par défaut en production
- Utiliser des clés aléatoires de 32+ caractères
- Les secrets Docker ont des permissions restrictives (chmod 400)
- Le filesystem est montné read_only pour les conteneurs web
- L'utilisateur est non-root (UID 1000)
- Les capacités Linux sont réduites (cap_drop ALL)