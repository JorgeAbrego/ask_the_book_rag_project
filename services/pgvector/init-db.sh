#!/bin/bash
set -e

# Check if environment variables are defined
if [ -z "$PG_VECTOR_PWD" ]; then
  echo "ERROR: One or more environment variables for passwords are not defined."
  exit 1
fi

# Create users and databases
PGPASSWORD=$POSTGRES_PASSWORD psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER vector_user WITH PASSWORD '$PG_VECTOR_PWD' SUPERUSER;
    CREATE DATABASE vector_db
        WITH 
        OWNER = vector_user
        ENCODING = 'UTF8'
        LC_COLLATE = 'en_US.utf8'
        LC_CTYPE = 'en_US.utf8'
        TABLESPACE = pg_default;
EOSQL

PGPASSWORD=$PG_VECTOR_PWD psql -v ON_ERROR_STOP=1 --username vector_user --dbname vector_db <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS vector;
EOSQL

PGPASSWORD=$POSTGRES_PASSWORD psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    ALTER USER vector_user NOSUPERUSER;
EOSQL