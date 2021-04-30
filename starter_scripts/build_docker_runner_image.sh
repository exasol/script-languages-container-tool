#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
PROJECT_ROOT_DIR="$SCRIPT_DIR/.."

IMAGE_NAME="$("$SCRIPT_DIR/construct_docker_runner_image_name.sh")"

docker build -t "$IMAGE_NAME" -f "$SCRIPT_DIR/Dockerfile" "$PROJECT_ROOT_DIR" 1>&2

echo "$IMAGE_NAME"