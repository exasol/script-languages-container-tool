#!/usr/bin/env bash

set -euo pipefail

[[ "$(uname)" = Darwin ]] && rl=greadlink || rl=readlink

if [[ ! "$(command -v $rl)" ]]; then
  echo readlink not available! Please install coreutils: On Linux \"apt-get install coreutils\" or similar. On MacOsX \"brew install coreutils\".
  exit 1
fi

SCRIPT_DIR="$(dirname "$($rl -f "${BASH_SOURCE[0]}")")"


RUNNER_IMAGE_NAME="$1"
shift 1

FIND_IMAGE_LOCALLY=$(docker images -q "$RUNNER_IMAGE_NAME")
if [ -z "$FIND_IMAGE_LOCALLY" ]; then
  docker pull "$RUNNER_IMAGE_NAME"
fi

[[ "$(uname)" = Darwin ]] && EXEC_SCRIPT=exaslct_within_docker_container_slim.sh || EXEC_SCRIPT=exaslct_within_docker_container.sh
bash "$SCRIPT_DIR/$EXEC_SCRIPT" "$RUNNER_IMAGE_NAME" "${@}"
