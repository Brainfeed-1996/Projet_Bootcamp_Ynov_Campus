#!/bin/bash
# scripts/healthcheck/web-healthcheck.sh - Web service health check
# Used by Docker healthcheck for the web service
# Returns 0 on success, 1 on failure

set -euo pipefail

HEALTH_ENDPOINT="${HEALTH_ENDPOINT:-http://localhost:5000/health}"
TIMEOUT="${HEALTHCHECK_TIMEOUT:-5}"
MAX_RETRIES="${HEALTHCHECK_RETRIES:-1}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

check_health() {
    local retries=0
    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -fsS --max-time "$TIMEOUT" "$HEALTH_ENDPOINT" >/dev/null 2>&1; then
            log "Health check passed"
            return 0
        fi
        retries=$((retries + 1))
        if [ $retries -lt $MAX_RETRIES ]; then
            log "Health check failed, retrying ($retries/$MAX_RETRIES)..."
            sleep 1
        fi
    done
    log "Health check failed after $MAX_RETRIES attempts"
    return 1
}

# Also check readiness endpoint if available
check_readiness() {
    local readiness_endpoint="${READINESS_ENDPOINT:-http://localhost:5000/ready}"
    if curl -fsS --max-time "$TIMEOUT" "$readiness_endpoint" >/dev/null 2>&1; then
        log "Readiness check passed"
        return 0
    fi
    log "Readiness endpoint not available or failed (non-blocking)"
    return 0
}

main() {
    log "Starting web health check for $HEALTH_ENDPOINT"
    check_health
    check_readiness
}

main "$@"