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
    is_active     BOOLEAN      DEFAULT TRUE,
    created_at    TIMESTAMPTZ  DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS logs (
    id         SERIAL PRIMARY KEY,
    level      VARCHAR(20) NOT NULL CHECK (level IN ('DEBUG','INFO','WARNING','ERROR','CRITICAL')),
    message    TEXT NOT NULL,
    source     VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS analyses (
    id         SERIAL PRIMARY KEY,
    type       VARCHAR(50)  NOT NULL,
    input_data TEXT,
    result     TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index de performance pour le filtrage des logs
CREATE INDEX IF NOT EXISTS idx_logs_level  ON logs(level);
CREATE INDEX IF NOT EXISTS idx_logs_source ON logs(source);
CREATE INDEX IF NOT EXISTS idx_analyses_type ON analyses(type);
