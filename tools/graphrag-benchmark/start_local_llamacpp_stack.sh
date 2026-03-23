#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

CHAT_CONTAINER="${GRAPHRAG_LOCAL_CHAT_CONTAINER:-eduassist-graphrag-chat}"
IMAGE="${LLAMACPP_SERVER_IMAGE:-ghcr.io/ggml-org/llama.cpp:server-cuda}"

CHAT_PORT="${GRAPHRAG_LOCAL_CHAT_PORT:-18080}"
READY_TIMEOUT_SECONDS="${GRAPHRAG_LOCAL_READY_TIMEOUT_SECONDS:-480}"

CHAT_ALIAS="${GRAPHRAG_LOCAL_CHAT_MODEL:-qwen2.5:7b}"
EMBEDDING_API_BASE="${GRAPHRAG_LOCAL_EMBEDDING_API_BASE:-http://127.0.0.1:11435/v1}"

CHAT_MODEL_BLOB="${GRAPHRAG_LOCAL_CHAT_MODEL_BLOB:-/mnt/c/Users/edann/.ollama/models/blobs/sha256-2bada8a7450677000f678be90653b85d364de7db25eb5ea54136ada5f3933730}"

if [[ ! -f "${CHAT_MODEL_BLOB}" ]]; then
  echo "Chat model blob not found: ${CHAT_MODEL_BLOB}" >&2
  exit 1
fi

docker rm -f "${CHAT_CONTAINER}" >/dev/null 2>&1 || true

docker run -d --rm \
  --name "${CHAT_CONTAINER}" \
  --gpus=all \
  -p "${CHAT_PORT}:8080" \
  -v "$(dirname "${CHAT_MODEL_BLOB}"):/models" \
  "${IMAGE}" \
  -m "/models/$(basename "${CHAT_MODEL_BLOB}")" \
  --alias "${CHAT_ALIAS}" \
  --host 0.0.0.0 \
  --port 8080 \
  -np 1 \
  -ngl 999 \
  -c 8192 >/dev/null

wait_for_ready() {
  local container_name="$1"
  local port="$2"
  local elapsed=0

  until curl -fsS "http://127.0.0.1:${port}/health" >/dev/null 2>&1; do
    sleep 2
    elapsed=$((elapsed + 2))
    if (( elapsed >= READY_TIMEOUT_SECONDS )); then
      echo "Timed out waiting for ${container_name} on port ${port}" >&2
      docker logs --tail 120 "${container_name}" >&2 || true
      return 1
    fi
  done
}

wait_for_ready "${CHAT_CONTAINER}" "${CHAT_PORT}"

printf 'chat_api_base=http://127.0.0.1:%s/v1\n' "${CHAT_PORT}"
printf 'embedding_api_base=%s\n' "${EMBEDDING_API_BASE}"
printf 'chat_container=%s\n' "${CHAT_CONTAINER}"
