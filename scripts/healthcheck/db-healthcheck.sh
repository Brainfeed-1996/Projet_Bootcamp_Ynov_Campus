#!/bin/bash
# scripts/healthcheck/db-healthcheck.sh - Database health check
# Used by Docker healthcheck for the PostgreSQL service
# Returns 0 on success, 1 on failure

set -euo pipefail

POSTGRES_USER_FILE="${POSTGRES_USER_FILE:-/run/secrets/postgres_user}"
POSTGRES_DB="${POSTGRES_DB:-music_hall}"
TIMEOUT="${HEALTHCHECK_TIMEOUT:-5}"
MAX_RETRIES="${HEALTHCHECK_RETRIES:-3}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

get_user() {
    if [ -f "$POSTGRES_USER_FILE" ]; then
        cat "$POSTGRES_USER_FILE"
    else
        echo "${POSTGRES_USER:-appuser}"
    fi
}

check_db() {
    local user
    user=$(get_user)
    local retries=0

    while [ $retries -lt $MAX_RETRIES ]; do
        if pg_isready -U "$user" -d "$POSTGRES_DB" -q >/dev/null 2>&1; then
            log "Database health check passed (user: $user, db: $POSTGRES_DB)"
            return 0
        fi
        retries=$((retries + 1))
        if [ $retries -lt $MAX_RETRIES ]; then
            log "Database health check failed, retrying ($retries/$MAX_RETRIES)..."
            sleep 1
        fi
    done
    log "Database health check failed after $MAX_RETRIES attempts"
    return 1
}

check_connection() {
    local user
    user=$(get_user)
    if psql -U "$user" -d "$POSTGRES_DB" -c "SELECT 1;" >/dev/null 2>&1; then
        log "Database connection test passed"
        return 0
    fi
    log "Database connection test failed"
    return 1
}

main() {
    log "Starting database health check for $POSTGRES_DB"
    check_db
    check_connection
}

main "$@"