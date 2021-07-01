#!/usr/bin/env bash

set -e


if [ $# -lt 1 ]; then
    echo "You must provide environment as argument"
    exit 1
fi

CI_ENV="$1"
IMAGE_NAME="script-languages-container-test-env:${CI_ENV}"
SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

docker build -t "$IMAGE_NAME" "$SCRIPT_DIR/$CI_ENV"
docker container rm -f -v ci_env_test || true
#Need to mount docker socket as we use docker within the CI environment
#Also need to mount root directory of script-languages-container-tool because we want to test this commit
docker run  -v /var/run/docker.sock:/var/run/docker.sock -v ${SCRIPT_DIR}/..:/working_dir --name ci_env_test -t $IMAGE_NAME