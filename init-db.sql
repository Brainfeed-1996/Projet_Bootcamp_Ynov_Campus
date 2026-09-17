-- init-db.sql - Schéma d'amorçage de la base music_hall (PostgreSQL)
-- Exécuté une fois, au premier démarrage du volume postgres_data.
-- Ce script initialise une base vide : il ne migre pas les volumes existants et
-- ne contient aucune opération DROP/ALTER destructive.

BEGIN;

CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL,
    email         VARCHAR(120) NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    is_active     BOOLEAN      DEFAULT TRUE,
    created_at    TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS logs (
    id          SERIAL PRIMARY KEY,
    level       VARCHAR(20) NOT NULL,
    message     TEXT        NOT NULL,
    source      VARCHAR(100),
    created_at  TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analyses (
    id          SERIAL PRIMARY KEY,
    type        VARCHAR(50) NOT NULL,
    input_data  TEXT,
    result      TEXT,
    created_at  TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id            SERIAL PRIMARY KEY,
    action        VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id   INTEGER,
    details       TEXT,
    created_at    TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes déclarés par les modèles SQLAlchemy.
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users(username);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users(email);

CREATE INDEX IF NOT EXISTS ix_logs_level ON logs(level);
CREATE INDEX IF NOT EXISTS ix_logs_source ON logs(source);
CREATE INDEX IF NOT EXISTS ix_logs_created_at ON logs(created_at);
CREATE INDEX IF NOT EXISTS ix_logs_level_created_at ON logs(level, created_at);
CREATE INDEX IF NOT EXISTS ix_logs_source_created_at ON logs(source, created_at);
CREATE INDEX IF NOT EXISTS ix_logs_level_source_created_at
    ON logs(level, source, created_at);

COMMIT;
