#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${IMAGE_NAME:-mehup/ocr-service:latest}"
CONTAINER_NAME="${CONTAINER_NAME:-ocr-service}"
NETWORK_NAME="${DOCKER_NETWORK:-mehup-ai}"
HOST_PORT="${HOST_PORT:-8003}"

docker network inspect "${NETWORK_NAME}" >/dev/null 2>&1 || docker network create "${NETWORK_NAME}"
docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true

docker run -d \
  --name "${CONTAINER_NAME}" \
  --restart unless-stopped \
  --network "${NETWORK_NAME}" \
  -p "${HOST_PORT}:8003" \
  "${IMAGE_NAME}"

echo "Started ${CONTAINER_NAME}: http://127.0.0.1:${HOST_PORT}/health"
