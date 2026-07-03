#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${IMAGE_NAME:-mehup/ocr-service:latest}"

docker build -t "${IMAGE_NAME}" .
echo "Built ${IMAGE_NAME}"
