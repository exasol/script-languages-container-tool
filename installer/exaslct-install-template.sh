#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

RUNNER_IMAGE_NAME="<<<<RUNNER_IMAGE_NAME>>>>"

$SCRIPT_DIR/exaslct-within-docker-container "$RUNNER_IMAGE_NAME" "${@}"

