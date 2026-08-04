-- Docuwing PostgreSQL initialization script.
-- Creates separate databases / schemas for the App and Engine layers.
-- Runs once on first container startup.

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schemas for logical separation
CREATE SCHEMA IF NOT EXISTS app;
CREATE SCHEMA IF NOT EXISTS engine;

-- Grant usage
GRANT USAGE ON SCHEMA app TO docuwing;
GRANT USAGE ON SCHEMA engine TO docuwing;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA app TO docuwing;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA engine TO docuwing;

-- Default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA app GRANT ALL PRIVILEGES ON TABLES TO docuwing;
ALTER DEFAULT PRIVILEGES IN SCHEMA engine GRANT ALL PRIVILEGES ON TABLES TO docuwing;
