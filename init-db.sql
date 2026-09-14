-- init-db.sql - Schéma reproductible de la base music_hall (PostgreSQL)
-- Monté via docker-compose dans /docker-entrypoint-initdb.d/ (exécuté une fois,
-- au premier démarrage du volume postgres_data). L'application crée également les
-- tables via SQLAlchemy (CREATE TABLE IF NOT EXISTS), sans conflit avec ce script.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    email         VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    role          VARCHAR(20)  NOT NULL DEFAULT 'reader',
    is_active     BOOLEAN      DEFAULT TRUE,
    created_at    TIMESTAMPTZ  DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS logs (
    id          SERIAL PRIMARY KEY,
    occurred_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    level       VARCHAR(20)  NOT NULL CHECK (level IN ('DEBUG','INFO','WARNING','ERROR','CRITICAL')),
    message     TEXT         NOT NULL,
    source      VARCHAR(100),
    metadata    TEXT,
    created_at  TIMESTAMPTZ  DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS analyses (
    id              SERIAL PRIMARY KEY,
    log_id          INTEGER      NOT NULL REFERENCES logs(id) ON DELETE CASCADE,
    severity        VARCHAR(20)  NOT NULL CHECK (severity IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    category        VARCHAR(100) NOT NULL,
    summary         TEXT         NOT NULL,
    recommendations TEXT         NOT NULL,
    provider        VARCHAR(50)  NOT NULL,
    created_at      TIMESTAMPTZ  DEFAULT NOW()
);

-- Index de performance pour le filtrage
CREATE INDEX IF NOT EXISTS idx_logs_level       ON logs(level);
CREATE INDEX IF NOT EXISTS idx_logs_source      ON logs(source);
CREATE INDEX IF NOT EXISTS idx_logs_occurred_at ON logs(occurred_at);
CREATE INDEX IF NOT EXISTS idx_analyses_log_id  ON analyses(log_id);
CREATE INDEX IF NOT EXISTS idx_analyses_severity ON analyses(severity);
CREATE INDEX IF NOT EXISTS idx_analyses_provider ON analyses(provider);