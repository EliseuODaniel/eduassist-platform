#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$REPO_ROOT/.env}"
COMPOSE_FILE="${COMPOSE_FILE:-$REPO_ROOT/infra/compose/compose.yaml}"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

: "${POSTGRES_USER:=eduassist}"
: "${POSTGRES_DB:=eduassist}"
: "${MINIO_ROOT_USER:=minioadmin}"
: "${MINIO_ROOT_PASSWORD:=minioadmin123}"
: "${MINIO_BUCKET_DOCUMENTS:=documents}"
: "${COMPOSE_PROJECT_NAME:=eduassist-platform}"

BACKUP_DIR="${1:-}"
if [[ -z "$BACKUP_DIR" ]]; then
  echo "usage: $0 <backup-dir>" >&2
  exit 1
fi

if [[ ! -d "$BACKUP_DIR" ]]; then
  echo "backup directory not found: $BACKUP_DIR" >&2
  exit 1
fi

POSTGRES_DUMP_PATH="$BACKUP_DIR/postgres/${POSTGRES_DB}.dump"
MINIO_BUCKET_PATH="$BACKUP_DIR/minio/$MINIO_BUCKET_DOCUMENTS"
RESTORE_DB="${RESTORE_DB:-eduassist_restore_check}"
RESTORE_BUCKET="${RESTORE_BUCKET:-${MINIO_BUCKET_DOCUMENTS}-restore-check}"
NETWORK_NAME="${COMPOSE_PROJECT_NAME}_default"

if [[ ! -f "$POSTGRES_DUMP_PATH" ]]; then
  echo "postgres dump not found: $POSTGRES_DUMP_PATH" >&2
  exit 1
fi

if [[ ! -d "$MINIO_BUCKET_PATH" ]]; then
  echo "minio bucket backup not found: $MINIO_BUCKET_PATH" >&2
  exit 1
fi

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T postgres \
  psql -U "$POSTGRES_USER" -d postgres -v ON_ERROR_STOP=1 \
  -c "select pg_terminate_backend(pid) from pg_stat_activity where datname = '$RESTORE_DB' and pid <> pg_backend_pid();" \
  >/dev/null

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T postgres \
  psql -U "$POSTGRES_USER" -d postgres -v ON_ERROR_STOP=1 \
  -c "drop database if exists \"$RESTORE_DB\";" \
  >/dev/null

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T postgres \
  psql -U "$POSTGRES_USER" -d postgres -v ON_ERROR_STOP=1 \
  -c "create database \"$RESTORE_DB\";" \
  >/dev/null

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T postgres \
  pg_restore \
  -U "$POSTGRES_USER" \
  -d "$RESTORE_DB" \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  < "$POSTGRES_DUMP_PATH"

LIVE_COUNTS="$(
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T postgres \
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tA \
    -c "select json_build_object(
      'users', (select count(*) from identity.users),
      'students', (select count(*) from school.students),
      'grades', (select count(*) from academic.grades),
      'invoices', (select count(*) from finance.invoices),
      'documents', (select count(*) from documents.documents)
    )::text;"
)"

RESTORE_COUNTS="$(
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T postgres \
    psql -U "$POSTGRES_USER" -d "$RESTORE_DB" -tA \
    -c "select json_build_object(
      'users', (select count(*) from identity.users),
      'students', (select count(*) from school.students),
      'grades', (select count(*) from academic.grades),
      'invoices', (select count(*) from finance.invoices),
      'documents', (select count(*) from documents.documents)
    )::text;"
)"

if [[ "$LIVE_COUNTS" != "$RESTORE_COUNTS" ]]; then
  echo "restored postgres counts do not match live database" >&2
  echo "live:    $LIVE_COUNTS" >&2
  echo "restore: $RESTORE_COUNTS" >&2
  exit 1
fi

BACKUP_OBJECT_COUNT="$(find "$MINIO_BUCKET_PATH" -type f | wc -l | tr -d ' ')"

docker run --rm \
  --network "$NETWORK_NAME" \
  --entrypoint /bin/sh \
  -v "$BACKUP_DIR/minio:/backup" \
  minio/mc:latest \
  -lc "
    set -euo pipefail
    mc alias set local http://minio:9000 \"$MINIO_ROOT_USER\" \"$MINIO_ROOT_PASSWORD\" >/dev/null
    mc rb --force local/$RESTORE_BUCKET >/dev/null 2>&1 || true
    mc mb local/$RESTORE_BUCKET >/dev/null
    mc mirror --overwrite /backup/$MINIO_BUCKET_DOCUMENTS local/$RESTORE_BUCKET >/dev/null
    mc ls --recursive local/$RESTORE_BUCKET | wc -l
    mc rb --force local/$RESTORE_BUCKET >/dev/null
  " > "$BACKUP_DIR/.minio_restore_count"

RESTORE_OBJECT_COUNT="$(tr -d ' \n' < "$BACKUP_DIR/.minio_restore_count")"
rm -f "$BACKUP_DIR/.minio_restore_count"

if [[ "$BACKUP_OBJECT_COUNT" != "$RESTORE_OBJECT_COUNT" ]]; then
  echo "restored minio object count does not match backup" >&2
  echo "backup:  $BACKUP_OBJECT_COUNT" >&2
  echo "restore: $RESTORE_OBJECT_COUNT" >&2
  exit 1
fi

cat <<EOF
{
  "ok": true,
  "backup_dir": "$BACKUP_DIR",
  "restore_db": "$RESTORE_DB",
  "restore_bucket": "$RESTORE_BUCKET",
  "postgres_counts": $LIVE_COUNTS,
  "minio_object_count": $RESTORE_OBJECT_COUNT
}
EOF
