#!/bin/bash
set -e

# Check if environment variables are defined
if [ -z "$PG_AIRFLOW_PWD" ] || [ -z "$PG_APP_PWD" ]; then
  echo "ERROR: One or more environment variables for passwords are not defined."
  exit 1
fi

# Create users and databases
PGPASSWORD=$POSTGRES_PASSWORD psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER airflow_user WITH PASSWORD '$PG_AIRFLOW_PWD' CREATEDB;
    CREATE DATABASE airflow_db
        WITH 
        OWNER = airflow_user
        ENCODING = 'UTF8'
        LC_COLLATE = 'en_US.utf8'
        LC_CTYPE = 'en_US.utf8'
        TABLESPACE = pg_default;

    CREATE USER app_user WITH PASSWORD '$PG_APP_PWD' CREATEDB;
    CREATE DATABASE app_db
        WITH 
        OWNER = app_user
        ENCODING = 'UTF8'
        LC_COLLATE = 'en_US.utf8'
        LC_CTYPE = 'en_US.utf8'
        TABLESPACE = pg_default;
EOSQL

# Create tables in app_db
PGPASSWORD=$PG_APP_PWD psql -v ON_ERROR_STOP=1 --username "app_user" --dbname "app_db" <<-EOSQL
    CREATE TABLE requests (
        id TEXT PRIMARY KEY,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        model_used TEXT NOT NULL,
        prompt_tokens INTEGER NOT NULL,
        completion_tokens INTEGER NOT NULL,
        total_tokens INTEGER NOT NULL,
        response_time FLOAT NOT NULL,
        rating integer,
        feedback TEXT NOT NULL,
        eval_prompt_tokens INTEGER NOT NULL,
        eval_completion_tokens INTEGER NOT NULL,
        eval_total_tokens INTEGER NOT NULL,
        timestamp TIMESTAMP WITH TIME ZONE NOT NULL
    );

    CREATE TABLE feedback (
        id SERIAL PRIMARY KEY,
        question_id TEXT REFERENCES requests(id),
        feedback INTEGER NOT NULL,
        timestamp TIMESTAMP WITH TIME ZONE NOT NULL
    );
EOSQL