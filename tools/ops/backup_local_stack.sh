#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$REPO_ROOT/.env}"
COMPOSE_FILE="${COMPOSE_FILE:-$REPO_ROOT/infra/compose/compose.yaml}"
BACKUP_ROOT="${BACKUP_ROOT:-$REPO_ROOT/artifacts/backups}"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

: "${COMPOSE_PROJECT_NAME:=eduassist-platform}"
: "${POSTGRES_USER:=eduassist}"
: "${POSTGRES_DB:=eduassist}"
: "${MINIO_ROOT_USER:=minioadmin}"
: "${MINIO_ROOT_PASSWORD:=minioadmin123}"
: "${MINIO_BUCKET_DOCUMENTS:=documents}"

LABEL="${1:-$(date -u +%Y%m%dT%H%M%SZ)}"
TARGET_DIR="$BACKUP_ROOT/$LABEL"
POSTGRES_DIR="$TARGET_DIR/postgres"
MINIO_DIR="$TARGET_DIR/minio"
POSTGRES_DUMP_PATH="$POSTGRES_DIR/${POSTGRES_DB}.dump"
MINIO_BUCKET_PATH="$MINIO_DIR/$MINIO_BUCKET_DOCUMENTS"
MANIFEST_PATH="$TARGET_DIR/manifest.json"
NETWORK_NAME="${COMPOSE_PROJECT_NAME}_default"

mkdir -p "$POSTGRES_DIR" "$MINIO_DIR"

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps postgres >/dev/null
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps minio >/dev/null

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T postgres \
  pg_dump \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  -Fc \
  --no-owner \
  --no-privileges \
  > "$POSTGRES_DUMP_PATH"

docker run --rm \
  --network "$NETWORK_NAME" \
  --entrypoint /bin/sh \
  -v "$MINIO_DIR:/backup" \
  minio/mc:latest \
  -lc "
    set -euo pipefail
    mc alias set local http://minio:9000 \"$MINIO_ROOT_USER\" \"$MINIO_ROOT_PASSWORD\" >/dev/null
    mc mirror --overwrite local/$MINIO_BUCKET_DOCUMENTS /backup/$MINIO_BUCKET_DOCUMENTS >/dev/null
  "

POSTGRES_SHA256="$(sha256sum "$POSTGRES_DUMP_PATH" | awk '{print $1}')"
POSTGRES_SIZE_BYTES="$(wc -c < "$POSTGRES_DUMP_PATH" | tr -d ' ')"
MINIO_OBJECT_COUNT="$(find "$MINIO_BUCKET_PATH" -type f | wc -l | tr -d ' ')"
MINIO_TOTAL_BYTES="$(find "$MINIO_BUCKET_PATH" -type f -printf '%s\n' | awk '{sum += $1} END {print sum + 0}')"
CREATED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

cat > "$MANIFEST_PATH" <<EOF
{
  "label": "$LABEL",
  "created_at": "$CREATED_AT",
  "postgres": {
    "database": "$POSTGRES_DB",
    "dump_path": "postgres/${POSTGRES_DB}.dump",
    "sha256": "$POSTGRES_SHA256",
    "size_bytes": $POSTGRES_SIZE_BYTES
  },
  "minio": {
    "bucket": "$MINIO_BUCKET_DOCUMENTS",
    "path": "minio/$MINIO_BUCKET_DOCUMENTS",
    "object_count": $MINIO_OBJECT_COUNT,
    "total_bytes": $MINIO_TOTAL_BYTES
  }
}
EOF

printf '%s\n' "$TARGET_DIR"
