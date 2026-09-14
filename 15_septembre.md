# Jour 7 — Mardi 15 septembre : Intégration de l'IA & APIs REST

## Résumé exécutif

Ce jour est consacré à l'intégration de l'intelligence artificielle (LLM) dans l'analyse de logs de sécurité. Nous allons concevoir un système capable de transformer un log brut en un diagnostic JSON structuré, en utilisant un pattern d'architecture à trois couches : un **fournisseur** (abstraction), un **adaptateur** (implémentation concrète, ex: OpenAI ou Ollama), et un **schéma** (contrat de réponse). L'objectif est d'obtenir un endpoint REST `POST /logs/{id}/analyze` qui renvoie une alerte exploitable sans être couplé à un fournisseur spécifique.

## Objectifs pédagogiques

À la fin de cette session, le participant sera capable de :

- Intégrer un LLM via une API REST (OpenAI ou Ollama en local) dans un service Python.
- Contraindre la réponse d'un modèle à un JSON structuré (schéma de réponse).
- Désigner un pattern Fournisseur / Adaptateur pour découpler l'application du fournisseur d'IA.
- Exposer un endpoint REST `POST /logs/{id}/analyze` qui retourne un diagnostic structuré.
- Valider et tester le module avec plusieurs erreurs et tentatives d'attaque.

## Détaillage horaire

| Horaires | Thème | Description |
|----------|-------|-------------|
| 09h00 - 09h40 | LLM & IA appliquée au développement | Intégrer un LLM via API REST avec OpenAI ou Ollama en local ; contraindre la réponse à un JSON structuré |
| 09h40 - 10h30 | Script de communication avec une IA | Analyser un rapport d'erreur et générer un diagnostic automatique |
| 10h30 - 11h30 | Fil rouge · Jalon 7 | Analyser les logs stockés pour extraire des alertes de sécurité |
| 11h30 - 12h00 | Démonstration | Tester le module avec plusieurs erreurs et tentatives d'attaque |

## Concepts clés

### LLM (Large Language Model)

Un modèle de langage grand qui traite et génère du texte à partir d'un prompt. Dans notre contexte, il analyse un log et produit un diagnostic.

### API REST

Une interface HTTP exposée par un service (FastAPI, Flask, etc.) qui permet d'envoyer des requêtes et de recevoir des réponses au format JSON.

### Fournisseur

Abstraction logicielle représentant le service d'IA (OpenAI, Ollama, Anthropic, etc.). Il définit une interface commune : une méthode `analyze(prompt)` qui retourne une chaîne structurée.

### Adaptateur

Implémentation concrète du fournisseur pour un service spécifique. Par exemple, `OpenAIAdapter` qui appelle l'API OpenAI, ou `OllamaAdapter` qui communique avec Ollama en local. Chaque adaptateur implémente la même interface.

### Prompt

Le texte envoyé au modèle pour obtenir une réponse. Un bon prompt est précis, contient le format de réponse attendu et les contraintes nécessaires.

### Schéma

Le contrat de réponse : une structure JSON attendue (champs, types, valeurs possibles). Exemple : `{ "severity": "high", "category": "brute_force", "explanation": "..." }`. Le schéma est validé avant retours.

### Faux fournisseur

Un fournisseur de test (mock) qui retourne une réponse prédéfinie sans appeler un service réel. Il permet de tester l'application sans dépendance réseau ni clé API.

---

## Exemple d'architecture

```
┌─────────────────────────────────────────┐
│           Endpoint REST                 │
│   POST /logs/{id}/analyze               │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         AnalyzeService                  │
│   - Valide le schéma                    │
│   - Appelle le fournisseur               │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Fournisseur (interface)         │
│   analyze(prompt: str) -> str           │
└──────┬──────────────┬─────────────────────┘
       │              │
       ▼              ▼
┌────────────┐  ┌────────────┐
│OpenAI      │  │Ollama      │
│Adapter     │  │Adapter     │
└────────────┘  └────────────┘
```

Le code ne dépend jamais d'un fournisseur spécifique : on peut swap OpenAI contre Ollama sans modifier le reste de l'application.

## Livrables Jalon 7 — Definition of Done

### 1. Interface commune de fournisseur

Un fichier `providers/base.py` qui définit une classe abstraite ou une interface :

```python
from abc import ABC, abstractmethod

class IProvider(ABC):
    @abstractmethod
    def analyze(self, prompt: str) -> str:
        """Analyse un prompt et retourne une réponse structurée."""
        pass
```

### 2. Adaptateur OpenAI

Un fichier `providers/openai_adapter.py` :

```python
import os
import json
from openai import OpenAI
from .base import IProvider

class OpenAIAdapter(IProvider):
    def __init__(self, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def analyze(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content
```

### 3. Adaptateur Ollama

Un fichier `providers/ollama_adapter.py` :

```python
import requests
from .base import IProvider

class OllamaAdapter(IProvider):
    def __init__(self, model: str = "llama3.2"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def analyze(self, prompt: str) -> str:
        response = requests.post(self.url, json={
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }, timeout=60)
        response.raise_for_status()
        return response.json()["response"]
```

### 4. Faux fournisseur (mock)

Un fichier `providers/mock_provider.py` pour les tests :

```python
from .base import IProvider

class MockProvider(IProvider):
    def __init__(self, response: str):
        self._response = response

    def analyze(self, prompt: str) -> str:
        return self._response
```

### 5. Schéma de réponse validé

Un fichier `schemas/diagnostic.py` qui définit et valide le JSON :

```python
from pydantic import BaseModel, Field
from typing import Literal

class DiagnosticSchema(BaseModel):
    severity: Literal["low", "medium", "high", "critical"]
    category: str
    explanation: str
    indicators: list[str]
    recommendation: str
```

### 6. Prompt template

Un fichier `prompts/analyze.txt` :

```
Tu es un analyste de sécurité. Analyse le log suivant et retourne un JSON strict avec ces champs :
- severity : "low", "medium", "high" ou "critical"
- category : type d'attaque ou d'erreur (ex: "brute_force", "sql_injection", "error_500")
- explanation : explication concise en français
- indicators : liste des indices observés dans le log
- recommendation : recommandation de mitigation

Log :
{log}

Réponds UNIQUEMENT avec le JSON, sans texte supplémentaire.
```

### 7. AnalyzeService

Un fichier `services/analyze_service.py` :

```python
import json
from providers.base import IProvider
from schemas.diagnostic import DiagnosticSchema

class AnalyzeService:
    def __init__(self, provider: IProvider):
        self.provider = provider

    def analyze_log(self, log: str) -> DiagnosticSchema:
        prompt = self._build_prompt(log)
        raw_response = self.provider.analyze(prompt)
        data = json.loads(raw_response)
        return DiagnosticSchema(**data)

    def _build_prompt(self, log: str) -> str:
        with open("prompts/analyze.txt") as f:
            template = f.read()
        return template.format(log=log)
```

### 8. Endpoint REST

Dans l'application FastAPI :

```python
from fastapi import FastAPI, HTTPException
from services.analyze_service import AnalyzeService
from providers.mock_provider import MockProvider

app = FastAPI()
service = AnalyzeService(MockProvider('{"severity":"high","category":"brute_force","explanation":"...","indicators":["..."],"recommendation":"..."}'))

@app.post("/logs/{log_id}/analyze")
async def analyze_log(log_id: str, log: str):
    try:
        diagnostic = service.analyze_log(log)
        return {"log_id": log_id, "diagnostic": diagnostic.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Definition of Done

- [ ] L'interface `IProvider` est créée et respectée par tous les adaptateurs.
- [ ] Les adaptateurs OpenAI et Ollama fonctionnent (testés avec un prompt simple).
- [ ] Le schéma `DiagnosticSchema` est défini et valide un JSON d'exemple.
- [ ] Le prompt template est prêt et interpolation du log fonctionne.
- [ ] L'endpoint `POST /logs/{id}/analyze` retourne un JSON structuré.
- [ ] Les tests avec le mock provider passent sans appeler de réseau ou clé API.
- [ ] Le code est organisésous `providers/`, `schemas/`, `services/`, `prompts/`.

## Erreurs fréquentes

### 1. Envoyer tout un fichier de logs au lieu de quelques champs

Le prompt doit recevoir un log ciblé, pas un fichier entier de plusieurs milliers de lignes. Le modèle a une limite de tokens (contexte) et perdra en précision si le log est trop long.

**Solution** : Pré-extraire les champs pertinents (timestamp, level, message, source_ip) avant d'envoyer au LLM. Utiliser un pré-filtre ou un summarizeur.

### 2. Supposer qu'un modèle répondra toujours un JSON valide

Les LLM ne sont pas fiables à 100% pour produire un JSON strict. Ils peuvent ajouter du texte, oublier un champ, ou mal formater.

**Solution** :
- Utiliser un prompt très explicite : "Réponds UNIQUEMENT avec le JSON, sans texte supplémentaire."
- Valider la réponse avec Pydantic (`DiagnosticSchema`).
- En cas d'erreur, réessayer avec un prompt modifié ou retourner une réponse par défaut.

### 3. Faire dépendre les tests d'un réseau ou d'une clé API réelle

Les tests unitaires doivent être rapides et indépendants de l'environnement extérieur.

**Solution** : Utiliser le `MockProvider` pour les tests. Ne testez les adaptateurs réels (OpenAI, Ollama) que dans des tests d'intégration dédiés, ou avec des enregistrements (VCR, responses).

### 4. Coupler directement l'API OpenAI dans le code métier

Incorporer `openai.OpenAI()` directement dans le service Analyze crée une dépendance forte.

**Solution** : Appliquer le pattern Fournisseur / Adaptateur. Le service ne connait que l'interface `IProvider`.

### 5. Oublier de gérer les timeouts et erreurs réseau

Un appel à un service externe peut échouer (timeout, erreur 5xx, clé API invalide).

**Solution** :
- Définir un timeout explicite (ex: 60s).
- Utiliser `try/except` pour gérer les erreurs.
- Implémenter un retry avec backoff exponentiel pour les erreurs transitoires.

## Connexions avec les jours suivants

### Jour 8 (Mercredi 16 septembre) — Dashboard & Visualisation
Les diagnostics JSON produits aujourd'hui alimentront un dashboard de visualisation (Grafana ou dashboard interne). Chaque alerte pourra être affichée avec sa sévérité, catégorie et recommandation.

### Jour 9 (Jeudi 17 septembre) — Orchestration & Automatisation
Le service d'analyse pourra être appelé par un workflow d'orchestration (Airflow, Prefect) pour analyser les logs en batch chaque nuit. Les alertes critiques pourront déclencher des actions automatiques (notification Slack, blocage IP).

### Jour 10 (Vendredi 18 septembre) — Bilan & Amélioration
Les retours des alertes (true/false positives) serviront à fine-tuner les prompts et le schéma. On pourra même entraîner un modèle local (Ollama) sur des logs historiques pour améliorer la précision.

## Pour aller plus loin

### Outils et commandes utiles

** Installer Ollama (local) **
```bash
# Télécharger et installer Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Démarrer le service Ollama
ollama serve &

# Télécharger un modèle local
ollama pull llama3.2

# Tester le modèle
ollama run llama3.2 "Analyse ce log : ..."
```

** Installer les dépendances Python **
```bash
pip install fastapi pydantic openai requests uvicorn
```

** Lancer l'API FastAPI **
```bash
uvicorn main:app --reload --port 8000
```

** Tester l'endpoint **
```bash
curl -X POST "http://localhost:8000/logs/1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"log": "2024-01-01 10:00:00 ERROR sshd[123]: Failed password for root from 192.168.1.1"}'
```

** Variables d'environnement **
```bash
export OPENAI_API_KEY="sk-..."
export OLLAMA_BASE_URL="http://localhost:11434"
```

### Bonnes pratiques

- Toujours valider le JSON avec Pydantic avant de le renvoyer.
- Garder les prompts dans des fichiers externes (`prompts/`) pour une facilité de maintenance.
- Utiliser le mock provider en développement et en test ; basculer sur OpenAI ou Ollama en production via une variable d'environnement.
- Mettre en place un logging structuré (JSON) pour tracer les appels LLM (prompt, réponse, latency).
- Considérer le caching : un même log produit souvent le même diagnostic ; éviter d'appeler l'API à chaque fois.
