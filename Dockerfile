# Dockerfile - Optimized production image
# Multi-stage build for minimal size
# Non-root runtime, read-only filesystem (managed by Compose)
# pip cache optimization, unnecessary files removed
# dumb-init for proper signal handling (PID 1)

# Build stage
FROM python:3.11-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Production stage
FROM python:3.11-slim AS production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/appuser/.local/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    dumb-init \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN useradd -m -u 1000 appuser

WORKDIR /app

COPY --from=builder /install /home/appuser/.local
COPY --chown=appuser:appuser . .

RUN chmod -R 755 /app

USER appuser:appuser

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=5 \
    CMD curl -fsS http://localhost:5000/health || exit 1

ENTRYPOINT ["dumb-init", "--"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]

# ---
# Optimizations:
# - Multi-stage build separates build deps from runtime
# - pip cache disabled, --prefix for clean install
# - Only runtime deps in final image (no build-essential)
# - Non-root user (appuser, UID 1000)
# - Filesystem mounted read_only by Compose
# - dumb-init handles signals (SIGTERM, etc.)
# - Vulnerabilities detected in CI by Trivy and Snyk
# ---