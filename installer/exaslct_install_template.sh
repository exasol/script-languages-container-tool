#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

RUNNER_IMAGE_NAME="<<<<RUNNER_IMAGE_NAME>>>>"

bash $SCRIPT_DIR/exaslct_within_docker_container_without_container_build.sh "$RUNNER_IMAGE_NAME" "${@}"

