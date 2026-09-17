# Guide de Sécurité

## Principes de Sécurité

### Defense in Depth
Le projet applique plusieurs couches de sécurité :

1. **Network** : Isolation Docker, pare-feu
2. **Application** : Validation, rate limiting, headers de sécurité
3. **Data** : Chiffrement, masquage, hachage
4. **Infrastructure** : Secrets management, scanning

### Architecture de S—curit—

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
?  ? — Non-root   ?  ? — Volume     ?  ? — TLS        ?             ?
?  ? — Read-only  ?  ?   persistant ?  ? — Policies   ?             ?
?  ? — Cap drop   ?  ? — TLS        ?  ? — Audit log  ?             ?
?  ? — Rate limit ?  ? — Backups    ?  ?              ?             ?
?  ? — JWT Auth   ?  ?              ?  ?              ?             ?
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

### Mod—le de Menaces (Threat Model - STRIDE)

| Menace | Description | Vecteur d'attaque | Impact | Probabilit— | Mitigation |
|--------|-------------|-------------------|--------|-------------|------------|
| **Spoofing** | Usurpation d'identit— utilisateur/API | Tokens JWT vol—s, credentials faibles | —lev— | Moyenne | JWT court (30min), bcrypt cost 12, rate limit auth 10/min |
| **Tampering** | Modification de logs/analyses | Injection SQL, mass assignment, CSV malveillant | —lev— | Faible | Validation Pydantic stricte, requ—tes param—tr—es, read-only FS |
| **Repudiation** | D—ni d'actions effectu—es | Absence de logs d'audit, suppression logs | Moyen | Moyenne | Audit logging immuable (7 ans), soft delete users |
| **Information Disclosure** | Fuite de donn—es sensibles | Logs contenant secrets, erreurs verbeuses, /docs expos— | —lev— | Moyenne | Redaction patterns (IP, email, tokens), headers s—curit—, pas de secrets en logs |
| **Denial of Service** | Indisponibilit— service | Payloads volumineux, boucles LLM, DB exhaustion | —lev— | Moyenne | Request size limit (10MB), bulk limit (10k), rate limiting, timeouts LLM |
| **Elevation of Privilege** | —l—vation de privil—ges | IDOR, bypass auth, role confusion | —lev— | Faible | Validation ID > 0, checks is_active, pas de role escalation API |

#---

## Threat Model D—taill—

### Sc—narios de Menaces par Domaine

#### Domaine : Authentification et Identification

| Sc—nario | ATT&CK T1078 | Description | Impact | Probabilit— | Mitigation | Test de validation |
|----------|-------------|-------------|--------|-------------|------------|-------------------|
| **Force brute sur /auth/login** | T1110.001 | Attaques par dictionnaire sur les credentials | —lev— | Faible | Rate limit 10/min, lockout apr—s 5 —checs, bcrypt cost 12 | `pytest tests/test_security.py::test_brute_force_protection` |
| **JWT replay** | T1550.001 | Vol et r—utilisation de token JWT | —lev— | Moyenne | Expiration 30min, rotation de cl—, `jti` claim unique | `pytest tests/test_security.py::test_jwt_replay_prevention` |
| **Credential stuffing** | T1078 | R—utilisation de creds leak—es | —lev— | Moyenne | Bcrypt unique par user, MFA pr—vue v1.3 | Rotation secrets trimestrielle |
| **—num—ration d'users** | T1087 | Scanning `/users/{id}` pour d—couvrir des IDs | Moyen | Moyenne | R—ponses uniformes (404), rate limit sur GET /users | V—rifier r—ponse identique pour user existant/inexistant |

#### Domaine : Ingestion de Logs

| Sc—nario | ATT&CK T1071.001 | Description | Impact | Probabilit— | Mitigation | Test de validation |
|----------|-------------------|-------------|--------|-------------|------------|-------------------|
| **Injection dans message de log** | T1059.001 | Logs contenant du code ex—cutable | —lev— | Faible | Escaping des sorties, validation regex, sandbox LLM | `pytest tests/test_security.py::test_log_injection` |
| **CSV injection (formulaire)** | T1235 | Fichier CSV contenant `=cmd|...` | Moyen | Moyenne | Pr—fixe `'=` dans les cellules, sandbox | `pytest tests/test_logs.py::test_csv_injection_rejection` |
| **Upload fichier malveillant** | T1105 | Fichier `.py` ou `.sh` d—guis— en `.csv` | Critique | Faible | Extension whitelist `.csv`, MIME check, antivirus | V—rifier seuls `.csv` accept—s |
| **Payload > 10 MB** | T1499 | DoS via upload massif | —lev— | Moyenne | `max_upload_size=10MB` dans middleware | Tester upload 11MB ? 413 |

#### Domaine : Analyse IA

| Sc—nario | ATT&CK T1235 | Description | Impact | Probabilit— | Mitigation | Test de validation |
|----------|-------------|-------------|--------|-------------|------------|-------------------|
| **Prompt injection** | T1235 | Log contenant des instructions pour le LLM | —lev— | Moyenne | Sanitization pre-LLM, sandbox r—sultat, validation sch—ma | `pytest tests/test_providers.py::test_prompt_injection_safety` |
| **Exfiltration via LLM** | T1048.003 | Donn—es sortantes via r—ponses LLM | Critique | Faible | Pattern blocklist PII, rate limit sortie | `pytest tests/test_security.py::test_llm_output_sanitization` |
| **Agent IA d—tourn—** | T1059 | R—sultat LLM ex—cut— comme commande | Critique | Tr—s faible | R—sultat LLM jamais ex—cut—, trait— comme donn—es | V—rifier `eval()` jamais appel— |

#### Domaine : Infrastructure et Secrets

| Sc—nario | ATT&CK T1078 | Description | Impact | Probabilit— | Mitigation | Test de validation |
|----------|-------------|-------------|--------|-------------|------------|-------------------|
| **Secret dans Git** | T1078 | Cl— API ou password commit— | Critique | Faible | `.gitignore`, git-secrets pre-commit, trufflehog CI | `pre-commit run --all-files` |
| **Docker escape** | T1068 | Conteneur root acc—de — host | Critique | Tr—s faible | Non-root (UID 1000), `cap_drop ALL`, read-only FS | Trivy scan image |
| **Vol de token Vault** | T1003.001 | Lecture des secrets Vault | Critique | Faible | AppRole TTL 1h, audit logging, r—seau isol— | V—rifier policies Vault |

### Cha—nes d'Attaque (Attack Chains)

#### Chain 1 : Compromission compl—te via Rate Limit Bypass

```
[1] Scanner les endpoints (T1595.002)
    ?
[2] Trouver endpoint sans rate limit (T1046)
    ?
[3] DoS par volume de requ—tes (T1499)
    ?
[4] Exploiter la charge pour masquer d'autres attaques (T1498)
    ?
[5] Injection SQL via requ—tes en bulk (T1190)
    ?
[6] Exfiltration de donn—es (T1041)
```

**Mitigation :** Rate limit global + par IP, WAF, monitoring anomalies.

#### Chain 2 : Escalade via LLM Provider

```
[1] Injecter prompt dans log message (T1235)
    ?
[2] Analyser le log ? LLM ex—cute l'instruction cach—e (T1059)
    ?
[3] LLM retourne des secrets dans le r—sultat (T1048)
    ?
[4] R—ponse de l'API expose les secrets (T1048.003)
```

**Mitigation :** Sanitization pre-LLM, sandboxing, validation de sortie.

#### Chain 3 : Vol de Secrets via Supply Chain

```
[1] Compromettre un package npm/pip d—pendant (T1195.002)
    ?
[2] Code malveillant lit les variables d'env (T1005)
    ?
[3] Envoi des secrets vers serveur externe (T1048)
    ?
[4] Utilisation des secrets pour acc—der — Vault (T1003.001)
```

**Mitigation :** `pip-audit` CI, d—pendances pin—es, r—seau egress restrictif.

### Mapping MITRE ATT&CK (S—lection Cl—)

| Technique ID | Technique | Tactic | Pr—sence dans le projet | Contr—le |
|-------------|-----------|---------|------------------------|----------|
| T1078.003 | Cloud Accounts | Initial Access | JWT auth | Expiration + rotation |
| T1059.001 | PowerShell / Shell | Execution | Logs contenus | Sandbox + validation |
| T1071.001 | Web Protocols | C2 | HTTP API | TLS + rate limit |
| T1003.001 | OS Credential Dumping | Credential Access | Secrets Vault | AppRole + audit |
| T1005 | Data from Local System | Collection | Fichiers read-only | FS permissions |
| T1048.003 | Exfiltration Over Unencrypted Non-C2 Protocol | Exfiltration | R—ponses API | Redaction PII |
| T1190 | Exploit Public-Facing Application | Initial Access | API endpoints | Validation Pydantic |
| T1195.002 | Supply Chain Compromise | Supply Chain | D—pendances | pip-audit, Trivy |
| T1235 | Data Manipulation | Impact | Logs/Analyses | Schema validation |
| T1499 | Endpoint Denial of Service | Impact | Rate limiting | Limites par endpoint |
| T1550.001 | Application Access Token | Persistence | JWT tokens | Court TTL (30min) |
| T1068 | Exploitation for Privilege Escalation | Privilege Escalation | Docker escape | Non-root, cap_drop |

### Enrichissement du mod—le STRIDE existant avec contr—les techniques

| Menace STRIDE | Contr—le technique | Outil | Fr—quence | Statut |
|---------------|-------------------|-------|-----------|--------|
| Spoofing | JWT + bcrypt + rate limit | Custom middleware | Continu | ? |
| Tampering | Validation Pydantic + requ—tes param—tr—es | SQLAlchemy | Continu | ? |
| Repudiation | Audit logs immuables | Loki (7 ans) | Continu | ? |
| Information Disclosure | Redaction middleware + headers | Custom middleware | Continu | ? |
| DoS | Rate limit + size limits + timeouts | Custom middleware | Continu | ? |
| Elevation | IDOR validation + role checks | Route dependencies | Continu | ? |
| **Nouveau :** CSRF | CSRF token sur state-changing ops | FastAPI middleware | Continu | ? Pr—vu v1.3 |
| **Nouveau :** Open Redirect | Validation URL de redirection | Validator | Continu | ? Pr—vu v1.3 |
| **Nouveau :** Insecure Deserialization | D—sactivation pickle, JSON uniquement | Config | Continu | ? |

---

## Matrice de Risques (Risk Matrix)

| Probabilit— \ Impact | Faible | Moyen | —lev— | Critique |
|---------------------|--------|-------|-------|----------|
| **Tr—s probable** | - | Rate limit bypass | DoS via bulk | - |
| **Probable** | Info disclosure logs | JWT replay | SQLi tentative | - |
| **Peu probable** | - | CSV injection | Privilege escalation | Supply chain |
| **Rare** | - | - | Vault compromise | Zero-day |

### Surface d'Attaque

| Composant | Ports expos—s | Authentification | Donn—es sensibles | Classification |
|-----------|---------------|------------------|-------------------|----------------|
| FastAPI Web | 5000 (HTTP) | JWT Bearer | Logs, users, analyses | Public API |
| PostgreSQL | 5432 (internal) | User/Pass + TLS | Tous les logs, users | Internal |
| Vault | 8200 (internal) | Token + TLS | Secrets (DB, API keys) | Internal |
| LLM Providers | 443 (external) | API Key | Prompts logs | External |
| Loki | 3100 (internal) | None (internal) | Logs agr—g—s | Internal |
| Prometheus | 9090 (internal) | None (internal) | M—triques | Internal |
| Jaeger | 16686 (internal) | None (internal) | Traces | Internal |

### Flux de Donn—es Sensibles

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
? SQLAlchemy       ?  ? Requ—tes param—tr—es, pas de concat—nation
? ORM / Raw SQL    ?
????????????????????
         ?
         ?
????????????????????
? PostgreSQL       ?  ? Volume chiffr—, backups chiffr—s
? (TLS, Volume)    ?
????????????????????
         ?
         ?
????????????????????
? LLM Provider     ?  ? Timeout 30s, Fake fallback, pas de PII envoy—e
? (Analyze)        ?
????????????????????
         ?
         ?
????????????????????
? Response         ?  ? Redaction patterns appliqu—s
? Redaction        ?
????????????????????
         ?
         ?
   Client Response
```

---

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
## Checklist de D—ploiement

- [ ] Mettre — jour les d—pendances
- [ ] Ex—cuter les tests de s—curit—
- [ ] Configurer les variables d'environnement
- [ ] V—rifier les permissions Vault
- [ ] Sauvegarder la base de donn—es
- [ ] Surveiller les logs post-d—ploiement

## Headers de S—curit—

| Header | Valeur | Description |
|--------|--------|-------------|
| X-Content-Type-Options | nosniff | Emp—che le MIME sniffing |
| X-Frame-Options | DENY | Emp—che le clickjacking |
| X-XSS-Protection | 1; mode=block | Protection XSS |
| Referrer-Policy | strict-origin-when-cross-origin | Politique de referral |
| Content-Security-Policy | default-src 'self' | Politique CSP |

## Monitoring

### M—triques cl—s
- Taux d'erreurs : < 1%
- Latence P99 : < 200ms
- Disponibilit— : > 99.9%

### Alertes configur—es
- Erreurs 500 : Imm—diate
- Latence —lev—e : 5 minutes
- Base de donn—es lente : 2 minutes

## Sauvegarde et Restauration

### Sauvegarde automatique
```bash
pg_dump -h db music_hall > backup.sql
```

### Restauration
```bash
psql -h db music_hall < backup.sql
```

### Fr—quence
- Quotidienne : 3h du matin
- Hebdomadaire : Dimanche 2h
- Mensuelle : Premier du mois

## R—tention des Donn—es

| Type de donn—es | Dur—e de r—tention |
|-----------------|-------------------|
| Logs | 90 jours |
| Analyses | 90 jours |
| Utilisateurs | 365 jours |
| Logs d'audit | 7 ans |

Les donn—es sont supprim—es automatiquement apr—s la p—riode.

## Plan de R—ponse aux Incidents

1. **D—tection** : Alertes automatis—es
2. **Containment** : Isolation du syst—me affect—
3. **—radication** : Suppression de la menace
4. **Restauration** : Retour — la normale
5. **Am—lioration** : Revue post-incident

---

## Incident Response Runbook

Ce runbook d—taille les proc—dures op—rationnelles pour r—pondre aux incidents de s—curit— sur Log Sentinel API.

### 0. Proc—dure op—rationnelle

> Objectif : contenir rapidement l'impact, pr—server les preuves et restaurer un service v—rifiable sans d—truire les indices. Toutes les heures sont en UTC. Ne copiez jamais de secret, token ou donn—e personnelle dans le ticket d'incident.

#### 0.1 Ouvrir et qualifier l'incident

1. Cr—er un identifiant unique (`INC-AAAAMMJJ-XXX`) et un canal priv— d—di—.
2. Nommer un **Incident Commander (IC)** responsable des d—cisions, une personne en charge de la technique et une personne en charge de la communication.
3. Noter l'heure de d—tection, la source de l'alerte, les services touch—s, le p—rim—tre suppos— et le niveau de s—v—rit—.
4. Classer l'incident :

| Niveau | Crit—re d'entr—e | R—ponse cible | Exemple |
|--------|------------------|---------------|---------|
| **P0** | compromission active, fuite confirm—e, perte ou corruption de donn—es, indisponibilit— critique | 15 minutes | secret de production expos—, injection SQL r—ussie |
| **P1** | exploitation probable ou d—gradation majeure | 1 heure | bypass d'authentification, DoS efficace |
| **P2** | anomalie contenue ou tentative bloqu—e | 4 heures | scan, pic de 429, erreur isol—e |
| **P3** | —v—nement sans impact confirm— | 24 heures | rejet CSV, tentative de connexion —chou—e |

5. Ouvrir une chronologie partag—e. Chaque action doit avoir un horodatage, un auteur, une commande ou une d—cision et son r—sultat.

#### 0.2 Pr—server les preuves avant toute correction

- Capturer l'—tat des services et des conteneurs avant de red—marrer ou supprimer une ressource :

```bash
date -u +%FT%TZ
docker compose -f compose.yaml -f docker-compose.production.yml ps
docker compose -f compose.yaml -f docker-compose.production.yml logs --since=2h web > "INC-<id>_web_$(date -u +%Y%m%dT%H%M%SZ).log"
docker compose -f compose.yaml -f docker-compose.production.yml logs --since=2h db > "INC-<id>_db_$(date -u +%Y%m%dT%H%M%SZ).log"
```

- Exporter les m—triques et les traces pertinentes depuis Prometheus, Loki et Jaeger ; conserver les requ—tes utilis—es.
- Faire un snapshot ou un `pg_dump` de la base dans un emplacement contr—l—, chiffr— et limit— aux personnes autoris—es.
- Conserver les images, versions de d—ploiement, tags Git, identifiants de conteneurs et horodatages. Ne pas ex—cuter de nettoyage, rotation ou suppression tant que l'IC n'a pas valid— la pr—servation.
- Journaliser les acc—s aux preuves et appliquer le principe du moindre privil—ge. Une preuve ne doit jamais —tre modifi—e dans son emplacement d'origine.

#### 0.3 Contenir, —radiquer et restaurer

| Phase | Actions minimales | Crit—re de sortie |
|-------|-------------------|-------------------|
| **Containment** | retirer le token expos—, bloquer l'adresse ou la route abusive, activer le mode maintenance, isoler le composant touch— | l'attaque ne peut plus progresser ; le p—rim—tre est connu |
| **—radication** | corriger la cause racine, r—voquer les credentials, supprimer l'acc—s non autoris—, scanner l'image et les d—pendances | aucun indicateur de compromission actif ; les correctifs sont revus |
| **Restauration** | d—ployer une version connue saine, restaurer les donn—es depuis une sauvegarde valid—e, r—activer progressivement le trafic | `/health` est sain, les contr—les de s—curit— passent, le trafic est surveill— |
| **Surveillance renforc—e** | suivre erreurs, latence, authentification, ingestion, DB et providers pendant au moins 72 h pour un P0/P1 | aucun signal de r—cidive pendant la fen—tre d—finie |

Toute d—cision destructive (suppression de compte, rotation de cl—, restauration, purge) doit —tre approuv—e par l'IC et consign—e. Si la cause n'est pas comprise, privil—gier l'isolement — une correction empirique.

#### 0.4 Communication et escalade

- Publier un premier statut dans le canal d'incident avec : identifiant, niveau, impact connu, heure de d—but, IC, actions en cours et prochaine mise — jour.
- Pour P0, envoyer une mise — jour au moins toutes les 30 minutes ; pour P1, toutes les heures.
- La communication externe et la notification r—glementaire sont coordonn—es par les r—les Communication et Legal/Compliance. Ne jamais divulguer de d—tail technique ou de donn—e sensible avant validation.
- Escalader imm—diatement au CISO, — la direction et au responsable juridique pour une fuite de donn—es, une compromission de secret ou un impact client confirm—.

#### 0.5 Cl—ture et revue post-incident

L'IC ne cl—ture l'incident qu'apr—s v—rification de la sant—, des acc—s, des sauvegardes, des journaux et des alertes. Une revue post-incident doit avoir lieu sous 48 heures et produire :

- une chronologie valid—e et une cause racine ;
- l'impact mesur— (utilisateurs, donn—es, dur—e, disponibilit—) ;
- les actions correctives avec propri—taire et —ch—ance ;
- les r—gles de d—tection, tests de r—gression et exercices de simulation manquants ;
- la mise — jour du pr—sent runbook et des seuils d'alerte.

Les actions de suivi sont suivies comme des —l—ments de travail distincts ; une simple fermeture de ticket ne constitue pas une cl—ture op—rationnelle.

### 1. Classification des Incidents

| Niveau | Crit—res | Exemples | Temps de r—ponse | Escalade |
|--------|----------|----------|------------------|----------|
| **P0 - Critique** | Perte de donn—es, compromission active, service down | Injection SQL r—ussie, RCE, fuite secrets prod, DB corrompue | < 15 min | CISO, Direction, Client si donn—es PII |
| **P1 - Majeur** | D—gradation s—v—re, vuln—rabilit— exploit—e | DoS r—ussi, auth bypass, CVE HIGH en prod | < 1 heure | Lead Security, Tech Lead |
| **P2 - Mineur** | Anomalie d—tect—e, tentative bloqu—e | Scan d—tect—, rate limit d—clench—, erreur 500 isol—e | < 4 heures | Team Lead |
| **P3 - Informationnel** | —v—nement de s—curit— sans impact | Tentative login —chou—e, CSV malformed rejet— | < 24 heures | Log uniquement |

### 2. R—les et Responsabilit—s

| R—le | Responsable | Contact | Backup |
|------|-------------|---------|--------|
| **Incident Commander (IC)** | Tech Lead / Lead DevOps | Slack #incidents / Tel | Senior DevOps |
| **Security Analyst** | Lead Security | Slack #security | Senior Dev |
| **Communications** | Product Owner | Email/Slack | Scrum Master |
| **Forensics** | Senior Dev | Slack #forensics | DevOps |
| **Stakeholder Liaison** | Engineering Manager | Email/Teams | CTO |

### 3. Proc—dures par Type d'Incident

#### 3.1 Compromission de Secrets (API Keys, DB Password, JWT Secret)

**D—tection :**
- Alerte Vault : acc—s anormal
- Logs : requ—tes depuis IP inconnue avec credentials valides
- GitHub : secret scanning alert

**Actions Imm—diates (T+0 — T+15min) :**
```bash
# 1. R—voquer le secret compromis
vault kv delete secret/log-sentinel  # ou path sp—cifique

# 2. G—n—rer nouveau secret
openssl rand -hex 32 > new_secret.txt
vault kv put secret/log-sentinel secret_key=@new_secret.txt

# 3. Rotater les secrets Docker
docker compose -f compose.yaml -f docker-compose.production.yml exec web \
  sh -c 'echo "$NEW_SECRET" > /run/secrets/secret_key'

# 4. Red—marrer les pods web (rolling restart)
docker compose -f compose.yaml -f docker-compose.production.yml up -d --no-deps --scale web=3 web

# 5. Invalider tous les JWT existants (changer SECRET_KEY)
#    ? Force re-login de tous les utilisateurs
```

**Investigation (T+15min — T+2h) :**
- Analyser logs Vault : `vault audit log /var/log/vault_audit.log`
- V—rifier Git history : `git log --all --oneline --grep="secret\|key\|password" --since="30 days ago"`
- Scanner repo : `trufflehog git file://. --since-commit=HEAD~100`
- Identifier scope : quel secret, depuis quand, quelles donn—es acc—d—es

**R—cup—ration :**
- D—ployer nouveaux secrets partout (CI, prod, staging, dev)
- Mettre — jour `.env.production.example` avec placeholders
- Revue post-incident sous 48h

---

#### 3.2 Injection SQL / Manipulation de Donn—es

**D—tection :**
- Alertes WAF / rate limit anomalies
- Logs DB : erreurs syntaxe, requ—tes lentes, `UNION SELECT` patterns
- Donn—es inattendues en base (nouveaux users, logs modifi—s)

**Actions Imm—diates :**
```bash
# 1. Isoler la DB (couper trafic entrant sauf admin)
docker compose -f compose.yaml -f docker-compose.production.yml exec db \
  psql -U postgres -c "ALTER DATABASE log_sentinel CONNECTION LIMIT 1;"

# 2. Snapshot forensique
docker compose -f compose.yaml -f docker-compose.production.yml exec db \
  pg_dump -U postgres log_sentinel > forensics_dump_$(date +%s).sql

# 3. Analyser logs r—cents
docker compose logs web --since=2h | grep -E "(UNION|SELECT|DROP|INSERT|UPDATE|DELETE|--|;)" | head -50

# 4. V—rifier int—grit— donn—es
docker compose exec db psql -U postgres -d log_sentinel -c "
  SELECT count(*) FROM logs WHERE message LIKE '%UNION%';
  SELECT count(*) FROM users WHERE username LIKE '%'||chr(39)||'%';
"
```

**Investigation :**
- Identifier endpoint vuln—rable (logs + stack traces)
- Corriger validation Pydantic / requ—tes param—tr—es
- Scanner code : `semgrep --config=auto app.py --rule=sql-injection`

**R—cup—ration :**
- Restaurer depuis backup propre si donn—es corrompues
- D—ployer fix + tests de r—gression
- Monitoring renforc— 72h

---

#### 3.3 D—ni de Service (DoS / Resource Exhaustion)

**D—tection :**
- Alertes Prometheus : `cpu_usage > 90%`, `memory_usage > 90%`, `request_duration_p99 > 5s`
- Logs : burst de requ—tes depuis m—me IP/range
- Health check `/health` ? timeout ou 503

**Actions Imm—diates :**
```bash
# 1. Activer rate limiting strict (si pas d—j—)
#    V—rifier middleware RateLimitMiddleware dans app.py

# 2. Bloquer IPs abusives (au niveau LB/NGINX)
#    NGINX: deny 192.0.2.0/24; dans config

# 3. Scale horizontal d'urgence
docker compose -f compose.yaml -f docker-compose.production.yml up -d --scale web=6

# 4. Si DB satur—e : limiter connexions
docker compose exec db psql -U postgres -c "ALTER DATABASE log_sentinel CONNECTION LIMIT 50;"

# 5. Basculer LLM_PROVIDER=fake si analyse IA cause du DoS
docker compose exec web sh -c 'echo "fake" > /run/secrets/llm_provider'
docker compose restart web
```

**Investigation :**
- Analyser patterns : `docker compose logs web | awk '{print $1}' | sort | uniq -c | sort -nr | head -20`
- Identifier si cibl— (endpoint sp—cifique) ou volum—trique
- V—rifier si bulk ingestion `/logs/bulk` ou `/logs/ingest-csv` abus—

**R—cup—ration :**
- Ajuster rate limits permanents
- Ajouter WAF rules (fail2ban, Cloudflare, NGINX rate limiting)
- Test de charge post-fix

---

#### 3.4 Fuite de Donn—es Sensibles (PII, Logs, Analyses)

**D—tection :**
- DLP alert : patterns PII en sortie (email, IP, carte bancaire)
- Logs Loki/Grafana : requ—tes inhabituelles sur `/logs` ou `/analyses`
- Signalement utilisateur / audit externe

**Actions Imm—diates :**
```bash
# 1. Couper l'acc—s public si expos—
#    LB/NGINX: return 403 pour /logs, /analyses sauf IP allowlist

# 2. V—rifier redaction middleware (app.py SENSITIVE_PATTERNS)
grep -n "SENSITIVE_PATTERNS" app.py

# 3. Audit acc—s r—cents
docker compose logs web --since=24h | grep -E "(GET /logs|GET /analyses)" | awk '{print $3}' | sort | uniq -c

# 4. V—rifier permissions utilisateurs
docker compose exec db psql -U postgres -d log_sentinel -c "
  SELECT username, role, is_active, last_login FROM users WHERE is_active=true;
"
```

**Investigation :**
- Quantifier donn—es expos—es (combien, quel type, quelle p—riode)
- Identifier cause : bug redaction, endpoint non prot—g—, config erron—e
- Notification RGPD si donn—es personnelles (72h max)

**R—cup—ration :**
- Corriger le bug redaction / ajouter middleware manquant
- Purger caches CDN / proxy si donn—es mises en cache
- Revue code : tous les endpoints retournant des donn—es utilisateur

---

#### 3.5 Compromission Conteneur / Supply Chain

**D—tection :**
- Trivy/Snyk : CVE CRITICAL nouvelle dans image d—ploy—e
- Comportement anormal : processus inconnus, connexions sortantes suspectes
- Falco / runtime security alert

**Actions Imm—diates :**
```bash
# 1. Isoler le conteneur
docker pause <container_id>

# 2. Snapshot forensique
docker commit <container_id> forensics/log-sentinel-$(date +%s)
docker save forensics/log-sentinel-$(date +%s) > forensics_image.tar

# 3. Analyser image
trivy image forensics/log-sentinel-$(date +%s) --severity HIGH,CRITICAL
docker history forensics/log-sentinel-$(date +%s)

# 4. Redeploy image propre (tag pr—c—dent connu bon)
docker compose -f compose.yaml -f docker-compose.production.yml up -d --no-deps web
# ou rollback tag
docker tag log-sentinel:v1.0.0 log-sentinel:latest
docker compose up -d --no-deps web
```

**Investigation :**
- V—rifier Dockerfile : `COPY` suspects, `RUN curl | sh`, base image
- Scanner dependencies : `pip-audit -r requirements.txt`
- V—rifier CI : build compromise ? (GitHub Actions logs)

**R—cup—ration :**
- Rebuild depuis base image patch—e (`python:3.11-slim` latest)
- Pin versions dans requirements.txt
- Signer images (cosign/notary) pour production

---

#### 3.6 Attaque sur Fournisseur LLM (Prompt Injection, Data Exfiltration)

**D—tection :**
- Analyses retournant r—sultats anormaux (exfiltration prompts)
- Co—ts API anormaux (OpenAI billing alert)
- Logs provider : requ—tes depuis IP non autoris—e

**Actions Imm—diates :**
```bash
# 1. Basculer en mode fake imm—diatement
docker compose exec web sh -c 'echo "fake" > /run/secrets/llm_provider'
docker compose restart web

# 2. R—voquer cl— API compromise
#    OpenAI: https://platform.openai.com/account/api-keys ? Revoke
#    Vault: vault kv delete secret/log-sentinel/openai_api_key

# 3. G—n—rer nouvelle cl—, stocker dans Vault
vault kv put secret/log-sentinel openai_api_key="sk-new-..."
```

**Investigation :**
- Analyser prompts envoy—s : `docker compose logs web | grep "analyze" -A5 -B5`
- V—rifier validation input avant envoi LLM (sanitization)
- Review prompt template dans `providers/openai_provider.py`

**R—cup—ration :**
- Renforcer validation/sanitization pre-LLM
- Ajouter allowlist de patterns autoris—s dans prompts
- Monitoring co—ts API quotidiens

---

### 4. Playbooks de Containment Rapide

#### Isolation R—seau d'Urgence

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
# Dans app.py : v—rifier MAINTENANCE_MODE au d—marrage des routes write
```

#### Arr—t Propre d'Urgence

```bash
# Arr—ter web, garder DB/Vault/Monitoring
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
?? D—but : <timestamp UTC>
?? Type : <SQLi / DoS / Secret Leak / etc.>
?? Impact : <services affect—s, utilisateurs, donn—es>
?? Statut : <Investigating / Contained / Recovering / Resolved>
?? —quipe : IC=<name>, Security=<name>, Comms=<name>
?? War Room : <Slack channel / Zoom link>
?? Prochaine MAJ : <timestamp + 30min>
????????????????????????????????????
```

#### Notification Externe (si P0 avec donn—es clients)

- Email clients affect—s sous 24h (RGPD Art. 33)
- Autorit— de protection donn—es (CNIL) sous 72h
- Communication publique pr—par—e par Comms + Legal

---

### 6. Post-Incident Review (PIR)

**D—lai : 48h apr—s r—solution**

#### Template PIR

```markdown
# Post-Incident Review - INC-<YYYYMMDD>-<XXX>

## R—sum— Ex—cutif
- **Incident** : <type, niveau>
- **Dur—e** : <d—but ? fin> (<X>h<Y>m)
- **Impact** : <utilisateurs, donn—es, revenu, r—putation>
- **Cause Racine** : <5 Whys analysis>

## Chronologie
| Heure (UTC) | —v—nement | Action | Auteur |
|-------------|-----------|--------|--------|
| 14:23 | Alerte Prometheus CPU > 90% | Investigation d—marr—e | IC |
| 14:25 | DoS confirm— sur /logs/bulk | Rate limit activ— | Security |
| 14:30 | Scale web x3 | Containment | DevOps |
| 15:10 | Root cause identifi— | Fix d—ploy— | Dev |
| 15:45 | Trafic normalis— | Recovery | IC |

## Cause Racine (5 Whys)
1. Pourquoi DoS ? ? Bulk endpoint sans limite par IP
2. Pourquoi pas de limite ? ? Rate limiting global seulement
3. Pourquoi global seulement ? ? Oubli— lors impl—mentation
4. Pourquoi oubli— ? ? Pas de threat modeling sur bulk
5. Pourquoi pas de threat modeling ? ? Processus incomplet

## Actions Correctives
| Action | Owner | —ch—ance | Statut |
|--------|-------|----------|--------|
| Rate limit par IP sur /logs/bulk | Dev | J+2 | ?? En cours |
| Ajouter bulk dans threat model | Security | J+5 | ? Planifi— |
| Test de charge bulk endpoint | QA | J+7 | ? Planifi— |
| Alerting sur bulk ingestion rate | DevOps | J+3 | ?? En cours |

## Le—ons Apprises
- Ce qui a bien march— : ...
- Ce qui a —chou— : ...
- Surprises : ...
- Am—liorations process : ...
```

---

### 7. Outils et Contacts d'Urgence

#### Commandes de Diagnostic Rapide

```bash
# Sant— globale
make health          # ou script custom v—rifiant /health, DB, Vault, LLM

# Logs r—cents (derni—re heure)
docker compose logs --since=1h web > incident_logs_$(date +%s).log

# M—triques cl—s
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
| **H—bergement Cloud** | Support AWS/Azure/GCP | Console + Phone (Enterprise) |
| **Registre Docker** | Docker Hub / GHCR | Status page + Support |
| **Vault (HCP)** | HashiCorp Support | Portal + Slack Connect |
| **LLM Provider** | OpenAI / Ollama | Dashboard + Email |
| **Autorit— RGPD** | CNIL (France) | https://www.cnil.fr/fr/signalement-violation-donnees |

---

### 8. Checklist de Pr—paration (— Valider Mensuellement)

- [ ] Runbook r—vis— et — jour (derni—re r—vision : <date>)
- [ ] Contacts d'urgence v—rifi—s
- [ ] War room Slack/Zoom fonctionnel
- [ ] Backups test—s (restore drill trimestriel)
- [ ] Forensics image snapshot procedure document—e
- [ ] Cl—s de secours Vault g—n—r—es et stock—es hors site
- [ ] Playbooks containment test—s en staging
- [ ] —quipe form—e (tabletop exercise semestriel)
- [ ] Communication templates — jour
- [ ] L—gal/Compliance valid— processus notification

### 9. Exercices de Simulation (Tabletop)

#### Sc—narios d'Exercice Trimestriels

| Sc—nario | Niveau | Dur—e | Participants | Objectif |
|----------|--------|-------|--------------|----------|
| **Secret leak** | P0 | 30 min | IC, Security, DevOps | Tester rotation secrets + notification |
| **DoS simul—** | P1 | 45 min | IC, DevOps, QA | Tester scaling + rate limiting |
| **Fuite PII** | P0 | 60 min | IC, Legal, Comms | Tester RGPD notification |
| **Vault downtime** | P1 | 30 min | DevOps, Security | Tester fallback secrets |
| **DB corruption** | P0 | 45 min | DevOps, Security | Tester restauration backup |
| **Prompt injection** | P1 | 30 min | Dev, Security | Tester sandbox LLM |

#### Processus d'Exercice

```
1. Annonce du sc—nario (10 min)
   ? Le "facilitateur" annonce l'incident simul—
2. Investigation (15-30 min)
   ? L'—quipe diagnostique et contient (comme en r—el)
3. R—solution (15-20 min)
   ? L'—quipe applique les correctifs
4. Debrief (15-20 min)
   ? Revue des actions, identification des am—liorations
5. Rapport (1h apr—s)
   ? Document actionn— int—gr— au runbook
```

### 10. Automatisation de la R—ponse

#### Alertes Prometheus (D—tection Automatique)

```yaml
# prometheus-rules.yml
groups:
  - name: log-sentinel-incidents
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Taux d'erreurs > 5% depuis 2 minutes"
          runbook: "SECURITY_GUIDE.md#section-3"

      - alert: PossibleBruteForce
        expr: rate(http_requests_total{endpoint="/users"}[1m]) > 20
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Tentative brute force sur /users"

      - alert: DBConnectionsHigh
        expr: pg_stat_activity_count > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Connexions DB > 80%"

      - alert: LLMProviderDown
        expr: rate(llm_provider_errors[5m]) > 0.5
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Provider LLM en erreur"
```

#### Playbook d'Escalade Automatis—e

```yaml
# Escalation rules (pseudo-code)
IF alert.severity == "critical":
    1. Slack #incidents ( imm—diat )
    2. SMS IC ( apr—s 5 min si non ack )
    3. Email management ( apr—s 15 min )
    4. PagerDuty ( apr—s 20 min )
    
IF alert.severity == "warning":
    1. Slack #security ( imm—diat )
    2. Email on-call ( apr—s 30 min si non ack )
```

---

## Agr—gation des Logs

L'API envoie les logs vers Loki pour :
- Centralisation
- Recherche full-text
- Visualisation (Grafana)
- D—tection d'anomalies

Configuration :
- URL Loki : http://loki:3100
- Labels : level, source, category

## Distributed Tracing

L'API utilise OpenTelemetry pour :
- Tra—age des requ—tes
- Performance monitoring
- Debugging distribu—

Exporteur : Jaeger

## R—tention des Donn—es

| Type de donn—es | Dur—e de r—tention |
|-----------------|-------------------|
| Logs | 90 jours |
| Analyses | 90 jours |
| Utilisateurs | 365 jours |
| Logs d'audit | 7 ans |

Les donn—es sont supprim—es automatiquement apr—s la p—riode.

## Audit Logging

Toutes les op—rations sensibles sont logged :
- Cr—ation/Modification/Suppression
- Authentification
- Changements de r—le
- Acc—s aux donn—es sensibles

Les logs d'audit sont conserv—s 7 ans.
