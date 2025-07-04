-- Database Permissions Fix for AI Translator
-- إصلاح صلاحيات قاعدة البيانات للترجمان الآلي

-- Connect as postgres superuser first
-- \c postgres postgres

-- Drop existing database and user if they exist
DROP DATABASE IF EXISTS ai_translator;
DROP USER IF EXISTS ai_translator;

-- Create new user with proper permissions
CREATE USER ai_translator WITH ENCRYPTED PASSWORD 'ai_translator_pass2024';

-- Create database owned by the new user
CREATE DATABASE ai_translator OWNER ai_translator;

-- Grant all privileges on database
GRANT ALL PRIVILEGES ON DATABASE ai_translator TO ai_translator;

-- Connect to the new database
\c ai_translator

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO ai_translator;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ai_translator;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ai_translator;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ai_translator;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ai_translator;

-- Allow user to create tables
ALTER USER ai_translator CREATEDB;

-- Verify permissions
SELECT 
    datname as database,
    datacl as permissions
FROM pg_database 
WHERE datname = 'ai_translator';

SELECT 
    usename as username,
    usecreatedb as can_create_db,
    usesuper as is_superuser
FROM pg_user 
WHERE usename = 'ai_translator';

-- Test connection (this should work without errors)
-- PGPASSWORD='ai_translator_pass2024' psql -h localhost -U ai_translator -d ai_translator -c "SELECT 1;"

-- Instructions for manual execution:
-- 1. sudo -u postgres psql
-- 2. \i /path/to/this/file.sql
-- 3. \q