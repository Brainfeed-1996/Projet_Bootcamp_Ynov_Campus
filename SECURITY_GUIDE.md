# Guide de SÃ©curitÃ©

## Principes de SÃ©curitÃ©

### Defense in Depth
Le projet applique plusieurs couches de sÃ©curitÃ© :

1. **Network** : Isolation Docker, pare-feu
2. **Application** : Validation, rate limiting, headers de sÃ©curitÃ©
3. **Data** : Chiffrement, masquage, hachage
4. **Infrastructure** : Secrets management, scanning

### Architecture de Sécurité

```
???????????????????????????????????????????????????????????????????????
?                        EXTERNAL CLIENTS                             ?
?                    (curl, Swagger, Scripts)                         ?
???????????????????????????????????????????????????????????????????????
                              ? HTTPS/TLS
                              ?
???????????????????????????????????????????????????????????????????????
?                      REVERSE PROXY / LB                             ?
?              (NGINX / Traefik - TLS Termination)                   ?
???????????????????????????????????????????????????????????????????????
                              ?
                              ?
???????????????????????????????????????????????????????????????????????
?                      DOCKER NETWORK (isolated)                      ?
?  ????????????????  ????????????????  ????????????????             ?
?  ?   WEB APP    ?  ?  POSTGRES    ?  ?    VAULT     ?             ?
?  ?  (FastAPI)   ?  ?   (DB)       ?  ?  (Secrets)   ?             ?
?  ?              ?  ?              ?  ?              ?             ?
?  ? • Non-root   ?  ? • Volume     ?  ? • TLS        ?             ?
?  ? • Read-only  ?  ?   persistant ?  ? • Policies   ?             ?
?  ? • Cap drop   ?  ? • TLS        ?  ? • Audit log  ?             ?
?  ? • Rate limit ?  ? • Backups    ?  ?              ?             ?
?  ? • JWT Auth   ?  ?              ?  ?              ?             ?
?  ????????????????  ????????????????  ????????????????             ?
?         ?                 ?                 ?                      ?
?         ?????????????????????????????????????                      ?
?                           ?                                        ?
?              ??????????????????????????                            ?
?              ?   LLM PROVIDERS        ?                            ?
?              ?  (OpenAI / Ollama /    ?                            ?
?              ?   Fake - External)     ?                            ?
?              ??????????????????????????                            ?
???????????????????????????????????????????????????????????????????????
                              ?
                              ?
???????????????????????????????????????????????????????????????????????
?                    OBSERVABILITY STACK                              ?
?  ????????????  ????????????  ????????????  ????????????           ?
?  ?  LOKI    ?  ? PROMETHEUS? ?  JAEGER  ?  ? GRAFANA  ?           ?
?  ? (Logs)   ?  ? (Metrics)?  ? (Traces) ?  ? (Dash)   ?           ?
?  ????????????  ????????????  ????????????  ????????????           ?
???????????????????????????????????????????????????????????????????????
```

### Modèle de Menaces (Threat Model - STRIDE)

| Menace | Description | Vecteur d'attaque | Impact | Probabilité | Mitigation |
|--------|-------------|-------------------|--------|-------------|------------|
| **Spoofing** | Usurpation d'identité utilisateur/API | Tokens JWT volés, credentials faibles | Élevé | Moyenne | JWT court (30min), bcrypt cost 12, rate limit auth 10/min |
| **Tampering** | Modification de logs/analyses | Injection SQL, mass assignment, CSV malveillant | Élevé | Faible | Validation Pydantic stricte, requêtes paramétrées, read-only FS |
| **Repudiation** | Déni d'actions effectuées | Absence de logs d'audit, suppression logs | Moyen | Moyenne | Audit logging immuable (7 ans), soft delete users |
| **Information Disclosure** | Fuite de données sensibles | Logs contenant secrets, erreurs verbeuses, /docs exposé | Élevé | Moyenne | Redaction patterns (IP, email, tokens), headers sécurité, pas de secrets en logs |
| **Denial of Service** | Indisponibilité service | Payloads volumineux, boucles LLM, DB exhaustion | Élevé | Moyenne | Request size limit (10MB), bulk limit (10k), rate limiting, timeouts LLM |
| **Elevation of Privilege** | Élévation de privilèges | IDOR, bypass auth, role confusion | Élevé | Faible | Validation ID > 0, checks is_active, pas de role escalation API |

#---

## Threat Model Détaillé

### Scénarios de Menaces par Domaine

#### Domaine : Authentification et Identification

| Scénario | ATT&CK T1078 | Description | Impact | Probabilité | Mitigation | Test de validation |
|----------|-------------|-------------|--------|-------------|------------|-------------------|
| **Force brute sur /auth/login** | T1110.001 | Attaques par dictionnaire sur les credentials | Élevé | Faible | Rate limit 10/min, lockout après 5 échecs, bcrypt cost 12 | `pytest tests/test_security.py::test_brute_force_protection` |
| **JWT replay** | T1550.001 | Vol et réutilisation de token JWT | Élevé | Moyenne | Expiration 30min, rotation de clé, `jti` claim unique | `pytest tests/test_security.py::test_jwt_replay_prevention` |
| **Credential stuffing** | T1078 | Réutilisation de creds leakées | Élevé | Moyenne | Bcrypt unique par user, MFA prévue v1.3 | Rotation secrets trimestrielle |
| **Énumération d'users** | T1087 | Scanning `/users/{id}` pour découvrir des IDs | Moyen | Moyenne | Réponses uniformes (404), rate limit sur GET /users | Vérifier réponse identique pour user existant/inexistant |

#### Domaine : Ingestion de Logs

| Scénario | ATT&CK T1071.001 | Description | Impact | Probabilité | Mitigation | Test de validation |
|----------|-------------------|-------------|--------|-------------|------------|-------------------|
| **Injection dans message de log** | T1059.001 | Logs contenant du code exécutable | Élevé | Faible | Escaping des sorties, validation regex, sandbox LLM | `pytest tests/test_security.py::test_log_injection` |
| **CSV injection (formulaire)** | T1235 | Fichier CSV contenant `=cmd|...` | Moyen | Moyenne | Préfixe `'=` dans les cellules, sandbox | `pytest tests/test_logs.py::test_csv_injection_rejection` |
| **Upload fichier malveillant** | T1105 | Fichier `.py` ou `.sh` déguisé en `.csv` | Critique | Faible | Extension whitelist `.csv`, MIME check, antivirus | Vérifier seuls `.csv` acceptés |
| **Payload > 10 MB** | T1499 | DoS via upload massif | Élevé | Moyenne | `max_upload_size=10MB` dans middleware | Tester upload 11MB ? 413 |

#### Domaine : Analyse IA

| Scénario | ATT&CK T1235 | Description | Impact | Probabilité | Mitigation | Test de validation |
|----------|-------------|-------------|--------|-------------|------------|-------------------|
| **Prompt injection** | T1235 | Log contenant des instructions pour le LLM | Élevé | Moyenne | Sanitization pre-LLM, sandbox résultat, validation schéma | `pytest tests/test_providers.py::test_prompt_injection_safety` |
| **Exfiltration via LLM** | T1048.003 | Données sortantes via réponses LLM | Critique | Faible | Pattern blocklist PII, rate limit sortie | `pytest tests/test_security.py::test_llm_output_sanitization` |
| **Agent IA détourné** | T1059 | Résultat LLM exécuté comme commande | Critique | Très faible | Résultat LLM jamais exécuté, traité comme données | Vérifier `eval()` jamais appelé |

#### Domaine : Infrastructure et Secrets

| Scénario | ATT&CK T1078 | Description | Impact | Probabilité | Mitigation | Test de validation |
|----------|-------------|-------------|--------|-------------|------------|-------------------|
| **Secret dans Git** | T1078 | Clé API ou password commité | Critique | Faible | `.gitignore`, git-secrets pre-commit, trufflehog CI | `pre-commit run --all-files` |
| **Docker escape** | T1068 | Conteneur root accède à host | Critique | Très faible | Non-root (UID 1000), `cap_drop ALL`, read-only FS | Trivy scan image |
| **Vol de token Vault** | T1003.001 | Lecture des secrets Vault | Critique | Faible | AppRole TTL 1h, audit logging, réseau isolé | Vérifier policies Vault |

### Chaînes d'Attaque (Attack Chains)

#### Chain 1 : Compromission complète via Rate Limit Bypass

```
[1] Scanner les endpoints (T1595.002)
    ?
[2] Trouver endpoint sans rate limit (T1046)
    ?
[3] DoS par volume de requêtes (T1499)
    ?
[4] Exploiter la charge pour masquer d'autres attaques (T1498)
    ?
[5] Injection SQL via requêtes en bulk (T1190)
    ?
[6] Exfiltration de données (T1041)
```

**Mitigation :** Rate limit global + par IP, WAF, monitoring anomalies.

#### Chain 2 : Escalade via LLM Provider

```
[1] Injecter prompt dans log message (T1235)
    ?
[2] Analyser le log ? LLM exécute l'instruction cachée (T1059)
    ?
[3] LLM retourne des secrets dans le résultat (T1048)
    ?
[4] Réponse de l'API expose les secrets (T1048.003)
```

**Mitigation :** Sanitization pre-LLM, sandboxing, validation de sortie.

#### Chain 3 : Vol de Secrets via Supply Chain

```
[1] Compromettre un package npm/pip dépendant (T1195.002)
    ?
[2] Code malveillant lit les variables d'env (T1005)
    ?
[3] Envoi des secrets vers serveur externe (T1048)
    ?
[4] Utilisation des secrets pour accéder à Vault (T1003.001)
```

**Mitigation :** `pip-audit` CI, dépendances pinées, réseau egress restrictif.

### Mapping MITRE ATT&CK (Sélection Clé)

| Technique ID | Technique | Tactic | Présence dans le projet | Contrôle |
|-------------|-----------|---------|------------------------|----------|
| T1078.003 | Cloud Accounts | Initial Access | JWT auth | Expiration + rotation |
| T1059.001 | PowerShell / Shell | Execution | Logs contenus | Sandbox + validation |
| T1071.001 | Web Protocols | C2 | HTTP API | TLS + rate limit |
| T1003.001 | OS Credential Dumping | Credential Access | Secrets Vault | AppRole + audit |
| T1005 | Data from Local System | Collection | Fichiers read-only | FS permissions |
| T1048.003 | Exfiltration Over Unencrypted Non-C2 Protocol | Exfiltration | Réponses API | Redaction PII |
| T1190 | Exploit Public-Facing Application | Initial Access | API endpoints | Validation Pydantic |
| T1195.002 | Supply Chain Compromise | Supply Chain | Dépendances | pip-audit, Trivy |
| T1235 | Data Manipulation | Impact | Logs/Analyses | Schema validation |
| T1499 | Endpoint Denial of Service | Impact | Rate limiting | Limites par endpoint |
| T1550.001 | Application Access Token | Persistence | JWT tokens | Court TTL (30min) |
| T1068 | Exploitation for Privilege Escalation | Privilege Escalation | Docker escape | Non-root, cap_drop |

### Enrichissement du modèle STRIDE existant avec contrôles techniques

| Menace STRIDE | Contrôle technique | Outil | Fréquence | Statut |
|---------------|-------------------|-------|-----------|--------|
| Spoofing | JWT + bcrypt + rate limit | Custom middleware | Continu | ? |
| Tampering | Validation Pydantic + requêtes paramétrées | SQLAlchemy | Continu | ? |
| Repudiation | Audit logs immuables | Loki (7 ans) | Continu | ? |
| Information Disclosure | Redaction middleware + headers | Custom middleware | Continu | ? |
| DoS | Rate limit + size limits + timeouts | Custom middleware | Continu | ? |
| Elevation | IDOR validation + role checks | Route dependencies | Continu | ? |
| **Nouveau :** CSRF | CSRF token sur state-changing ops | FastAPI middleware | Continu | ? Prévu v1.3 |
| **Nouveau :** Open Redirect | Validation URL de redirection | Validator | Continu | ? Prévu v1.3 |
| **Nouveau :** Insecure Deserialization | Désactivation pickle, JSON uniquement | Config | Continu | ? |

---

## Matrice de Risques (Risk Matrix)

| Probabilité \ Impact | Faible | Moyen | Élevé | Critique |
|---------------------|--------|-------|-------|----------|
| **Très probable** | - | Rate limit bypass | DoS via bulk | - |
| **Probable** | Info disclosure logs | JWT replay | SQLi tentative | - |
| **Peu probable** | - | CSV injection | Privilege escalation | Supply chain |
| **Rare** | - | - | Vault compromise | Zero-day |

### Surface d'Attaque

| Composant | Ports exposés | Authentification | Données sensibles | Classification |
|-----------|---------------|------------------|-------------------|----------------|
| FastAPI Web | 5000 (HTTP) | JWT Bearer | Logs, users, analyses | Public API |
| PostgreSQL | 5432 (internal) | User/Pass + TLS | Tous les logs, users | Internal |
| Vault | 8200 (internal) | Token + TLS | Secrets (DB, API keys) | Internal |
| LLM Providers | 443 (external) | API Key | Prompts logs | External |
| Loki | 3100 (internal) | None (internal) | Logs agrégés | Internal |
| Prometheus | 9090 (internal) | None (internal) | Métriques | Internal |
| Jaeger | 16686 (internal) | None (internal) | Traces | Internal |

### Flux de Données Sensibles

```
User Input (JSON/CSV)
       ?
       ?
????????????????????
? Request Size     ?  ? 10 MB limit
? Limit Middleware ?
????????????????????
         ?
         ?
????????????????????
? Pydantic         ?  ? Validation stricte, whitelist levels
? Validation       ?
????????????????????
         ?
         ?
????????????????????
? SQLAlchemy       ?  ? Requêtes paramétrées, pas de concaténation
? ORM / Raw SQL    ?
????????????????????
         ?
         ?
????????????????????
? PostgreSQL       ?  ? Volume chiffré, backups chiffrés
? (TLS, Volume)    ?
????????????????????
         ?
         ?
????????????????????
? LLM Provider     ?  ? Timeout 30s, Fake fallback, pas de PII envoyée
? (Analyze)        ?
????????????????????
         ?
         ?
????????????????????
? Response         ?  ? Redaction patterns appliqués
? Redaction        ?
????????????????????
         ?
         ?
   Client Response
```

---

## Configuration SÃ©curisÃ©e

### Variables d'environnement sensibles
Les variables sensibles doivent Ãªtre :
- StockÃ©es dans `.env` (ignorÃ© par Git)
- Ou dans un vault (HashiCorp Vault)
- JAMAIS commitÃ©es dans le dÃ©pÃ´t

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

## Analyse de SÃ©curitÃ©

### Tests de pÃ©nÃ©tration
La suite de tests inclut :
- Injection SQL
- XSS
- Mass assignment
- Broken authentication
- Sensitive data exposure

### Scan de dÃ©pendances
```bash
# VÃ©rifier les vulnÃ©rabilitÃ©s
safety check -r requirements.txt
pip-audit -r requirements.txt
```

### Analyse de code
```bash
# Bandit pour la sÃ©curitÃ© Python
bandit -r app.py -f json -o bandit-report.json

# Semgrep pour l'analyse statique
semgrep --config=auto app.py
```

## Bonnes Pratiques

### Pour les dÃ©veloppeurs
1. Ne jamais commit de secrets
2. Utiliser `git rebase` pour un historique propre
3. Ã‰crire des tests pour chaque feature
4. Valider avec `pre-commit` avant de push

### Pour l'ops
1. Surveiller les logs d'audit
2. Mettre Ã  jour les dÃ©pendances rÃ©guliÃ¨rement
3. Sauvegarder la base de donnÃ©es
4. Faire des scans de sÃ©curitÃ© rÃ©guliers

### Pour les auditeurs
1. Consulter le rapport de sÃ©curitÃ© (`security_audit.md`)
2. VÃ©rifier les logs d'accÃ¨s
3. Auditer les permissions des utilisateurs
4. ContrÃ´ler la configuration Vault
## Checklist de Déploiement

- [ ] Mettre à jour les dépendances
- [ ] Exécuter les tests de sécurité
- [ ] Configurer les variables d'environnement
- [ ] Vérifier les permissions Vault
- [ ] Sauvegarder la base de données
- [ ] Surveiller les logs post-déploiement

## Headers de Sécurité

| Header | Valeur | Description |
|--------|--------|-------------|
| X-Content-Type-Options | nosniff | Empêche le MIME sniffing |
| X-Frame-Options | DENY | Empêche le clickjacking |
| X-XSS-Protection | 1; mode=block | Protection XSS |
| Referrer-Policy | strict-origin-when-cross-origin | Politique de referral |
| Content-Security-Policy | default-src 'self' | Politique CSP |

## Monitoring

### Métriques clés
- Taux d'erreurs : < 1%
- Latence P99 : < 200ms
- Disponibilité : > 99.9%

### Alertes configurées
- Erreurs 500 : Immédiate
- Latence élevée : 5 minutes
- Base de données lente : 2 minutes

## Sauvegarde et Restauration

### Sauvegarde automatique
```bash
pg_dump -h db music_hall > backup.sql
```

### Restauration
```bash
psql -h db music_hall < backup.sql
```

### Fréquence
- Quotidienne : 3h du matin
- Hebdomadaire : Dimanche 2h
- Mensuelle : Premier du mois

## Rétention des Données

| Type de données | Durée de rétention |
|-----------------|-------------------|
| Logs | 90 jours |
| Analyses | 90 jours |
| Utilisateurs | 365 jours |
| Logs d'audit | 7 ans |

Les données sont supprimées automatiquement après la période.

## Plan de Réponse aux Incidents

1. **Détection** : Alertes automatisées
2. **Containment** : Isolation du système affecté
3. **Éradication** : Suppression de la menace
4. **Restauration** : Retour à la normale
5. **Amélioration** : Revue post-incident

---

## Incident Response Runbook

Ce runbook détaille les procédures opérationnelles pour répondre aux incidents de sécurité sur Log Sentinel API.

### 1. Classification des Incidents

| Niveau | Critères | Exemples | Temps de réponse | Escalade |
|--------|----------|----------|------------------|----------|
| **P0 - Critique** | Perte de données, compromission active, service down | Injection SQL réussie, RCE, fuite secrets prod, DB corrompue | < 15 min | CISO, Direction, Client si données PII |
| **P1 - Majeur** | Dégradation sévère, vulnérabilité exploitée | DoS réussi, auth bypass, CVE HIGH en prod | < 1 heure | Lead Security, Tech Lead |
| **P2 - Mineur** | Anomalie détectée, tentative bloquée | Scan détecté, rate limit déclenché, erreur 500 isolée | < 4 heures | Team Lead |
| **P3 - Informationnel** | Événement de sécurité sans impact | Tentative login échouée, CSV malformed rejeté | < 24 heures | Log uniquement |

### 2. Rôles et Responsabilités

| Rôle | Responsable | Contact | Backup |
|------|-------------|---------|--------|
| **Incident Commander (IC)** | Tech Lead / Lead DevOps | Slack #incidents / Tel | Senior DevOps |
| **Security Analyst** | Lead Security | Slack #security | Senior Dev |
| **Communications** | Product Owner | Email/Slack | Scrum Master |
| **Forensics** | Senior Dev | Slack #forensics | DevOps |
| **Stakeholder Liaison** | Engineering Manager | Email/Teams | CTO |

### 3. Procédures par Type d'Incident

#### 3.1 Compromission de Secrets (API Keys, DB Password, JWT Secret)

**Détection :**
- Alerte Vault : accès anormal
- Logs : requêtes depuis IP inconnue avec credentials valides
- GitHub : secret scanning alert

**Actions Immédiates (T+0 à T+15min) :**
```bash
# 1. Révoquer le secret compromis
vault kv delete secret/log-sentinel  # ou path spécifique

# 2. Générer nouveau secret
openssl rand -hex 32 > new_secret.txt
vault kv put secret/log-sentinel secret_key=@new_secret.txt

# 3. Rotater les secrets Docker
docker compose -f compose.yaml -f docker-compose.production.yml exec web \
  sh -c 'echo "$NEW_SECRET" > /run/secrets/secret_key'

# 4. Redémarrer les pods web (rolling restart)
docker compose -f compose.yaml -f docker-compose.production.yml up -d --no-deps --scale web=3 web

# 5. Invalider tous les JWT existants (changer SECRET_KEY)
#    ? Force re-login de tous les utilisateurs
```

**Investigation (T+15min à T+2h) :**
- Analyser logs Vault : `vault audit log /var/log/vault_audit.log`
- Vérifier Git history : `git log --all --oneline --grep="secret\|key\|password" --since="30 days ago"`
- Scanner repo : `trufflehog git file://. --since-commit=HEAD~100`
- Identifier scope : quel secret, depuis quand, quelles données accédées

**Récupération :**
- Déployer nouveaux secrets partout (CI, prod, staging, dev)
- Mettre à jour `.env.production.example` avec placeholders
- Revue post-incident sous 48h

---

#### 3.2 Injection SQL / Manipulation de Données

**Détection :**
- Alertes WAF / rate limit anomalies
- Logs DB : erreurs syntaxe, requêtes lentes, `UNION SELECT` patterns
- Données inattendues en base (nouveaux users, logs modifiés)

**Actions Immédiates :**
```bash
# 1. Isoler la DB (couper trafic entrant sauf admin)
docker compose -f compose.yaml -f docker-compose.production.yml exec db \
  psql -U postgres -c "ALTER DATABASE log_sentinel CONNECTION LIMIT 1;"

# 2. Snapshot forensique
docker compose -f compose.yaml -f docker-compose.production.yml exec db \
  pg_dump -U postgres log_sentinel > forensics_dump_$(date +%s).sql

# 3. Analyser logs récents
docker compose logs web --since=2h | grep -E "(UNION|SELECT|DROP|INSERT|UPDATE|DELETE|--|;)" | head -50

# 4. Vérifier intégrité données
docker compose exec db psql -U postgres -d log_sentinel -c "
  SELECT count(*) FROM logs WHERE message LIKE '%UNION%';
  SELECT count(*) FROM users WHERE username LIKE '%'||chr(39)||'%';
"
```

**Investigation :**
- Identifier endpoint vulnérable (logs + stack traces)
- Corriger validation Pydantic / requêtes paramétrées
- Scanner code : `semgrep --config=auto app.py --rule=sql-injection`

**Récupération :**
- Restaurer depuis backup propre si données corrompues
- Déployer fix + tests de régression
- Monitoring renforcé 72h

---

#### 3.3 Déni de Service (DoS / Resource Exhaustion)

**Détection :**
- Alertes Prometheus : `cpu_usage > 90%`, `memory_usage > 90%`, `request_duration_p99 > 5s`
- Logs : burst de requêtes depuis même IP/range
- Health check `/health` ? timeout ou 503

**Actions Immédiates :**
```bash
# 1. Activer rate limiting strict (si pas déjà)
#    Vérifier middleware RateLimitMiddleware dans app.py

# 2. Bloquer IPs abusives (au niveau LB/NGINX)
#    NGINX: deny 192.0.2.0/24; dans config

# 3. Scale horizontal d'urgence
docker compose -f compose.yaml -f docker-compose.production.yml up -d --scale web=6

# 4. Si DB saturée : limiter connexions
docker compose exec db psql -U postgres -c "ALTER DATABASE log_sentinel CONNECTION LIMIT 50;"

# 5. Basculer LLM_PROVIDER=fake si analyse IA cause du DoS
docker compose exec web sh -c 'echo "fake" > /run/secrets/llm_provider'
docker compose restart web
```

**Investigation :**
- Analyser patterns : `docker compose logs web | awk '{print $1}' | sort | uniq -c | sort -nr | head -20`
- Identifier si ciblé (endpoint spécifique) ou volumétrique
- Vérifier si bulk ingestion `/logs/bulk` ou `/logs/ingest-csv` abusé

**Récupération :**
- Ajuster rate limits permanents
- Ajouter WAF rules (fail2ban, Cloudflare, NGINX rate limiting)
- Test de charge post-fix

---

#### 3.4 Fuite de Données Sensibles (PII, Logs, Analyses)

**Détection :**
- DLP alert : patterns PII en sortie (email, IP, carte bancaire)
- Logs Loki/Grafana : requêtes inhabituelles sur `/logs` ou `/analyses`
- Signalement utilisateur / audit externe

**Actions Immédiates :**
```bash
# 1. Couper l'accès public si exposé
#    LB/NGINX: return 403 pour /logs, /analyses sauf IP allowlist

# 2. Vérifier redaction middleware (app.py SENSITIVE_PATTERNS)
grep -n "SENSITIVE_PATTERNS" app.py

# 3. Audit accès récents
docker compose logs web --since=24h | grep -E "(GET /logs|GET /analyses)" | awk '{print $3}' | sort | uniq -c

# 4. Vérifier permissions utilisateurs
docker compose exec db psql -U postgres -d log_sentinel -c "
  SELECT username, role, is_active, last_login FROM users WHERE is_active=true;
"
```

**Investigation :**
- Quantifier données exposées (combien, quel type, quelle période)
- Identifier cause : bug redaction, endpoint non protégé, config erronée
- Notification RGPD si données personnelles (72h max)

**Récupération :**
- Corriger le bug redaction / ajouter middleware manquant
- Purger caches CDN / proxy si données mises en cache
- Revue code : tous les endpoints retournant des données utilisateur

---

#### 3.5 Compromission Conteneur / Supply Chain

**Détection :**
- Trivy/Snyk : CVE CRITICAL nouvelle dans image déployée
- Comportement anormal : processus inconnus, connexions sortantes suspectes
- Falco / runtime security alert

**Actions Immédiates :**
```bash
# 1. Isoler le conteneur
docker pause <container_id>

# 2. Snapshot forensique
docker commit <container_id> forensics/log-sentinel-$(date +%s)
docker save forensics/log-sentinel-$(date +%s) > forensics_image.tar

# 3. Analyser image
trivy image forensics/log-sentinel-$(date +%s) --severity HIGH,CRITICAL
docker history forensics/log-sentinel-$(date +%s)

# 4. Redeploy image propre (tag précédent connu bon)
docker compose -f compose.yaml -f docker-compose.production.yml up -d --no-deps web
# ou rollback tag
docker tag log-sentinel:v1.0.0 log-sentinel:latest
docker compose up -d --no-deps web
```

**Investigation :**
- Vérifier Dockerfile : `COPY` suspects, `RUN curl | sh`, base image
- Scanner dependencies : `pip-audit -r requirements.txt`
- Vérifier CI : build compromise ? (GitHub Actions logs)

**Récupération :**
- Rebuild depuis base image patchée (`python:3.11-slim` latest)
- Pin versions dans requirements.txt
- Signer images (cosign/notary) pour production

---

#### 3.6 Attaque sur Fournisseur LLM (Prompt Injection, Data Exfiltration)

**Détection :**
- Analyses retournant résultats anormaux (exfiltration prompts)
- Coûts API anormaux (OpenAI billing alert)
- Logs provider : requêtes depuis IP non autorisée

**Actions Immédiates :**
```bash
# 1. Basculer en mode fake immédiatement
docker compose exec web sh -c 'echo "fake" > /run/secrets/llm_provider'
docker compose restart web

# 2. Révoquer clé API compromise
#    OpenAI: https://platform.openai.com/account/api-keys ? Revoke
#    Vault: vault kv delete secret/log-sentinel/openai_api_key

# 3. Générer nouvelle clé, stocker dans Vault
vault kv put secret/log-sentinel openai_api_key="sk-new-..."
```

**Investigation :**
- Analyser prompts envoyés : `docker compose logs web | grep "analyze" -A5 -B5`
- Vérifier validation input avant envoi LLM (sanitization)
- Review prompt template dans `providers/openai_provider.py`

**Récupération :**
- Renforcer validation/sanitization pre-LLM
- Ajouter allowlist de patterns autorisés dans prompts
- Monitoring coûts API quotidiens

---

### 4. Playbooks de Containment Rapide

#### Isolation Réseau d'Urgence

```bash
# Couper tout trafic entrant vers web (sauf health check LB)
docker network disconnect log-sentinel_frontend web
# Ou au niveau LB/NGINX : upstream log_sentinel { down; }

# Maintenir DB accessible pour forensics
docker network connect log-sentinel_backend db
```

#### Mode "Maintenance" (Read-Only)

```bash
# Activer read-only sur API (via variable d'env ou feature flag)
docker compose exec web sh -c 'echo "true" > /run/secrets/maintenance_mode'
# Dans app.py : vérifier MAINTENANCE_MODE au démarrage des routes write
```

#### Arrêt Propre d'Urgence

```bash
# Arrêter web, garder DB/Vault/Monitoring
docker compose -f compose.yaml -f docker-compose.production.yml stop web

# Backup DB avant investigation
docker compose exec db pg_dump -U postgres log_sentinel > emergency_backup_$(date +%s).sql
```

---

### 5. Communication pendant l'Incident

#### Template de Status Update (Toutes les 30 min pour P0, 1h pour P1)

```
?? INCIDENT P<level> - Log Sentinel API
????????????????????????????????????
?? Début : <timestamp UTC>
?? Type : <SQLi / DoS / Secret Leak / etc.>
?? Impact : <services affectés, utilisateurs, données>
?? Statut : <Investigating / Contained / Recovering / Resolved>
?? Équipe : IC=<name>, Security=<name>, Comms=<name>
?? War Room : <Slack channel / Zoom link>
?? Prochaine MAJ : <timestamp + 30min>
????????????????????????????????????
```

#### Notification Externe (si P0 avec données clients)

- Email clients affectés sous 24h (RGPD Art. 33)
- Autorité de protection données (CNIL) sous 72h
- Communication publique préparée par Comms + Legal

---

### 6. Post-Incident Review (PIR)

**Délai : 48h après résolution**

#### Template PIR

```markdown
# Post-Incident Review - INC-<YYYYMMDD>-<XXX>

## Résumé Exécutif
- **Incident** : <type, niveau>
- **Durée** : <début ? fin> (<X>h<Y>m)
- **Impact** : <utilisateurs, données, revenu, réputation>
- **Cause Racine** : <5 Whys analysis>

## Chronologie
| Heure (UTC) | Événement | Action | Auteur |
|-------------|-----------|--------|--------|
| 14:23 | Alerte Prometheus CPU > 90% | Investigation démarrée | IC |
| 14:25 | DoS confirmé sur /logs/bulk | Rate limit activé | Security |
| 14:30 | Scale web x3 | Containment | DevOps |
| 15:10 | Root cause identifié | Fix déployé | Dev |
| 15:45 | Trafic normalisé | Recovery | IC |

## Cause Racine (5 Whys)
1. Pourquoi DoS ? ? Bulk endpoint sans limite par IP
2. Pourquoi pas de limite ? ? Rate limiting global seulement
3. Pourquoi global seulement ? ? Oublié lors implémentation
4. Pourquoi oublié ? ? Pas de threat modeling sur bulk
5. Pourquoi pas de threat modeling ? ? Processus incomplet

## Actions Correctives
| Action | Owner | Échéance | Statut |
|--------|-------|----------|--------|
| Rate limit par IP sur /logs/bulk | Dev | J+2 | ?? En cours |
| Ajouter bulk dans threat model | Security | J+5 | ? Planifié |
| Test de charge bulk endpoint | QA | J+7 | ? Planifié |
| Alerting sur bulk ingestion rate | DevOps | J+3 | ?? En cours |

## Leçons Apprises
- Ce qui a bien marché : ...
- Ce qui a échoué : ...
- Surprises : ...
- Améliorations process : ...
```

---

### 7. Outils et Contacts d'Urgence

#### Commandes de Diagnostic Rapide

```bash
# Santé globale
make health          # ou script custom vérifiant /health, DB, Vault, LLM

# Logs récents (dernière heure)
docker compose logs --since=1h web > incident_logs_$(date +%s).log

# Métriques clés
curl -s http://localhost:9090/api/v1/query?query=up | jq .
curl -s http://localhost:9090/api/v1/query?query=rate(http_requests_total[5m]) | jq .

# Processus suspects dans conteneur
docker compose exec web ps auxf
docker compose exec web netstat -tulpn
docker compose exec web lsof -i
```

#### Contacts

| Service | Contact | Moyens |
|---------|---------|--------|
| **Hébergement Cloud** | Support AWS/Azure/GCP | Console + Phone (Enterprise) |
| **Registre Docker** | Docker Hub / GHCR | Status page + Support |
| **Vault (HCP)** | HashiCorp Support | Portal + Slack Connect |
| **LLM Provider** | OpenAI / Ollama | Dashboard + Email |
| **Autorité RGPD** | CNIL (France) | https://www.cnil.fr/fr/signalement-violation-donnees |

---

### 8. Checklist de Préparation (À Valider Mensuellement)

- [ ] Runbook révisé et à jour (dernière révision : <date>)
- [ ] Contacts d'urgence vérifiés
- [ ] War room Slack/Zoom fonctionnel
- [ ] Backups testés (restore drill trimestriel)
- [ ] Forensics image snapshot procedure documentée
- [ ] Clés de secours Vault générées et stockées hors site
- [ ] Playbooks containment testés en staging
- [ ] Équipe formée (tabletop exercise semestriel)
- [ ] Communication templates à jour
- [ ] Légal/Compliance validé processus notification

## Agrégation des Logs

L'API envoie les logs vers Loki pour :
- Centralisation
- Recherche full-text
- Visualisation (Grafana)
- Détection d'anomalies

Configuration :
- URL Loki : http://loki:3100
- Labels : level, source, category

## Distributed Tracing

L'API utilise OpenTelemetry pour :
- Traçage des requêtes
- Performance monitoring
- Debugging distribué

Exporteur : Jaeger

## Rétention des Données

| Type de données | Durée de rétention |
|-----------------|-------------------|
| Logs | 90 jours |
| Analyses | 90 jours |
| Utilisateurs | 365 jours |
| Logs d'audit | 7 ans |

Les données sont supprimées automatiquement après la période.

## Audit Logging

Toutes les opérations sensibles sont logged :
- Création/Modification/Suppression
- Authentification
- Changements de rôle
- Accès aux données sensibles

Les logs d'audit sont conservés 7 ans.
