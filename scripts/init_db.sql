-- Database initialization script for ZenRows API
-- This script runs when the PostgreSQL container starts for the first time

-- Create the database if it doesn't exist (though it should already exist from POSTGRES_DB)
-- This is just a safety measure
SELECT 'CREATE DATABASE zenrows_api'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'zenrows_api')\gexec

-- Set timezone
SET timezone = 'UTC';

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE zenrows_api TO zenrows_user;
