#!/usr/bin/env bash
set -euo pipefail

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  SELECT 'CREATE DATABASE ${POSTGRES_KEYCLOAK_DB}'
  WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${POSTGRES_KEYCLOAK_DB}')\gexec
EOSQL

