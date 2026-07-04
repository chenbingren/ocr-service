#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${IMAGE_NAME:-mehup/ocr-service:latest}"
CONTAINER_NAME="${CONTAINER_NAME:-ocr-service}"
BUILD_IMAGE="${BUILD_IMAGE:-true}"
RUN_CONTAINER="${RUN_CONTAINER:-true}"
DOCKER_NETWORK="${DOCKER_NETWORK:-}"
HOST_PORT="${HOST_PORT:-8003}"
FILE_DATA_DIR="${FILE_DATA_DIR:-/data/app/file_data}"
CONTAINER_FILE_DATA_DIR="${CONTAINER_FILE_DATA_DIR:-/data/app/file_data}"

if [[ "${BUILD_IMAGE}" != "false" ]]; then
  docker build -t "${IMAGE_NAME}" .
  echo "Built ${IMAGE_NAME}"
fi

if [[ "${RUN_CONTAINER}" == "false" ]]; then
  exit 0
fi

DOCKER_ARGS=()
if [[ -n "${DOCKER_NETWORK}" ]]; then
  docker network inspect "${DOCKER_NETWORK}" >/dev/null 2>&1 || docker network create "${DOCKER_NETWORK}"
  DOCKER_ARGS+=(--network "${DOCKER_NETWORK}")
fi

docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true

docker run -d \
  --name "${CONTAINER_NAME}" \
  --restart unless-stopped \
  "${DOCKER_ARGS[@]}" \
  -p "${HOST_PORT}:8003" \
  -v "${FILE_DATA_DIR}:${CONTAINER_FILE_DATA_DIR}:ro" \
  "${IMAGE_NAME}"

echo "Started ${CONTAINER_NAME}: http://127.0.0.1:${HOST_PORT}/health"
