#!/usr/bin/env bash

set -euo pipefail

if [ -n "${1-}" ]; then
  image_suffix="$1"
else
  image_suffix="latest"
fi

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

GIT_IMAGE_NAME="$("$SCRIPT_DIR/build_docker_runner_image.sh")"

docker push "$GIT_IMAGE_NAME"

RENAMED_IMAGE_NAME="$("$SCRIPT_DIR/construct_docker_runner_image_name.sh" "$image_suffix")"

docker tag "$GIT_IMAGE_NAME" "$RENAMED_IMAGE_NAME"

docker push "$RENAMED_IMAGE_NAME"
