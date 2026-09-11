# Dockerfile - Image de production sécurisée
# Runtime non-root, filesystem en lecture-seule (géré par Compose)
# Le scan Trivy est exécuté dans le pipeline CI, pas dans l'image de build
# Utilise dumb-init pour la gestion correcte des signaux (PID 1)

FROM python:3.11-slim AS production

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    dumb-init \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R appuser:appuser /app && \
    chmod -R 755 /app

USER appuser:appuser

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=5 \
    CMD curl -fsS http://localhost:5000/health || exit 1

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["dumb-init", "--"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]

# ---
# Limites :
# - L'utilisateur est non-root (appuser, UID 1000)
# - Le filesystem est monté read_only par Compose (read_only: true)
# - Les vulnérabilités sont détectées en CI par Trivy et Snyk
# - dumb-init gère correctement les signaux (SIGTERM, etc.)
# ---
