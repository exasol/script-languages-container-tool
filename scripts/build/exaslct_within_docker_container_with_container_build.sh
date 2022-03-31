#!/usr/bin/env bash

#####################################################################################
###REMEMBER TO TEST ANY CHANGES HERE ON MACOSX!!!
#####################################################################################

set -euo pipefail

rl=readlink
if [[ "$(uname)" = Darwin ]]; then
  rl=greadlink
fi

if [[ ! "$(command -v $rl)" ]]; then
  echo readlink not available! Please install coreutils: On Linux \"apt-get install coreutils\" or similar. On MacOsX \"brew install coreutils\".
  exit 1
fi

SCRIPT_DIR="$(dirname "$($rl -f "${BASH_SOURCE[0]}")")"
PROJECT_ROOT_DIR="$SCRIPT_DIR/../.."
STARTER_SCRIPT_DIR="$PROJECT_ROOT_DIR/exasol_script_languages_container_tool/starter_scripts"

RUNNER_IMAGE_NAME="$1"
shift 1

if [[ -z "${EXASLCT_FORCE_REBUILD:-}" ]]; then
  echo "Searching local image...."
  FIND_IMAGE_LOCALLY=$(docker images -q "$RUNNER_IMAGE_NAME")
  if [ -z "$FIND_IMAGE_LOCALLY" ]; then
    echo "Not found local image. Let's pull or rebuild it."
    docker pull "$RUNNER_IMAGE_NAME" || bash "$SCRIPT_DIR/build_docker_runner_image.sh"
  fi
else
  echo "Force rebuild image set...."
  bash "$SCRIPT_DIR/build_docker_runner_image.sh"
fi

BASH_MAJOR_VERSION=$(echo "${BASH_VERSION}" | cut -f1 -d".")

EXEC_SCRIPT=exaslct_within_docker_container.sh
if [[ "$(uname)" = Darwin ]] || [[ $BASH_MAJOR_VERSION -lt 4 ]]; then
  EXEC_SCRIPT=exaslct_within_docker_container_slim.sh
fi


bash "$STARTER_SCRIPT_DIR/$EXEC_SCRIPT" "$RUNNER_IMAGE_NAME" "${@}"
