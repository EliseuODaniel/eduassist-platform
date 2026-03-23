#!/usr/bin/env bash
set -euo pipefail

CHAT_CONTAINER="${GRAPHRAG_LOCAL_CHAT_CONTAINER:-eduassist-graphrag-chat}"
EMBED_CONTAINER="${GRAPHRAG_LOCAL_EMBED_CONTAINER:-eduassist-graphrag-embed}"

docker rm -f "${CHAT_CONTAINER}" "${EMBED_CONTAINER}" >/dev/null 2>&1 || true
echo "Stopped ${CHAT_CONTAINER} and ${EMBED_CONTAINER}."
