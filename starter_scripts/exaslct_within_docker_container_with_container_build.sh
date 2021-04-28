#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

RUNNER_IMAGE_NAME="$1"
shift 1

docker pull "$RUNNER_IMAGE_NAME" || bash "$SCRIPT_DIR/build_docker_runner_image.sh"

bash "$SCRIPT_DIR/exaslct_within_docker_container.sh" "$RUNNER_IMAGE_NAME" "${@}"