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
: "${QDRANT_PORT:=6333}"
: "${QDRANT_DOCUMENTS_COLLECTION:=school_documents}"
: "${MINIO_ROOT_USER:=minioadmin}"
: "${MINIO_ROOT_PASSWORD:=minioadmin123}"
: "${MINIO_BUCKET_DOCUMENTS:=documents}"

LABEL="${1:-$(date -u +%Y%m%dT%H%M%SZ)}"
TARGET_DIR="$BACKUP_ROOT/$LABEL"
POSTGRES_DIR="$TARGET_DIR/postgres"
QDRANT_DIR="$TARGET_DIR/qdrant"
MINIO_DIR="$TARGET_DIR/minio"
POSTGRES_DUMP_PATH="$POSTGRES_DIR/${POSTGRES_DB}.dump"
QDRANT_HOST_URL="${QDRANT_URL_LOCAL:-http://localhost:${QDRANT_PORT}}"
MINIO_BUCKET_PATH="$MINIO_DIR/$MINIO_BUCKET_DOCUMENTS"
MANIFEST_PATH="$TARGET_DIR/manifest.json"
NETWORK_NAME="${COMPOSE_PROJECT_NAME}_default"

mkdir -p "$POSTGRES_DIR" "$QDRANT_DIR" "$MINIO_DIR"

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

QDRANT_SNAPSHOT_NAME="$(
  curl -fsS -X POST "${QDRANT_HOST_URL}/collections/${QDRANT_DOCUMENTS_COLLECTION}/snapshots?wait=true" \
    | python3 -c 'import sys, json; print(json.load(sys.stdin)["result"]["name"])'
)"
QDRANT_SNAPSHOT_PATH="$QDRANT_DIR/$QDRANT_SNAPSHOT_NAME"
curl -fsS \
  -o "$QDRANT_SNAPSHOT_PATH" \
  "${QDRANT_HOST_URL}/collections/${QDRANT_DOCUMENTS_COLLECTION}/snapshots/${QDRANT_SNAPSHOT_NAME}"

QDRANT_POINTS_COUNT="$(
  curl -fsS "${QDRANT_HOST_URL}/collections/${QDRANT_DOCUMENTS_COLLECTION}" \
    | python3 -c 'import sys, json; print(int(json.load(sys.stdin)["result"]["points_count"]))'
)"

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
QDRANT_SHA256="$(sha256sum "$QDRANT_SNAPSHOT_PATH" | awk '{print $1}')"
QDRANT_SIZE_BYTES="$(wc -c < "$QDRANT_SNAPSHOT_PATH" | tr -d ' ')"
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
  "qdrant": {
    "collection": "$QDRANT_DOCUMENTS_COLLECTION",
    "snapshot_path": "qdrant/$QDRANT_SNAPSHOT_NAME",
    "sha256": "$QDRANT_SHA256",
    "size_bytes": $QDRANT_SIZE_BYTES,
    "points_count": $QDRANT_POINTS_COUNT
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
