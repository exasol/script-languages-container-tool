#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

bash "$SCRIPT_DIR/../../starter_scripts/build_docker_runner_image.sh"

INSTALLER_DIRECTORY="$SCRIPT_DIR/.."
STARTER_DIRECTORY="$SCRIPT_DIR/../../starter_scripts"

MYTMPDIR="$(mktemp -d)"
trap 'rm -rf -- "$MYTMPDIR"' EXIT

GIT_REF=$(git rev-parse HEAD)


cp "$INSTALLER_DIRECTORY/exaslct_install_template.sh" "$MYTMPDIR/exaslct_install_template.sh"
#Here we copy the same files as in ../exaslct_installer.sh
#Take care and make sure list of files is identical!!!
cp "$STARTER_DIRECTORY/exaslct_within_docker_container_without_container_build.sh" "$MYTMPDIR/exaslct_within_docker_container_without_container_build.sh"
cp "$STARTER_DIRECTORY/exaslct_within_docker_container.sh" "$MYTMPDIR/exaslct_within_docker_container.sh"
cp "$STARTER_DIRECTORY/construct_docker_runner_image_name.sh" "$MYTMPDIR/construct_docker_runner_image_name.sh"
cp "$STARTER_DIRECTORY/mount_point_parsing.sh" "$MYTMPDIR/mount_point_parsing.sh"

sed -i "s/<<<<EXASLCT_GIT_REF>>>>/$GIT_REF/g" "$MYTMPDIR/exaslct_install_template.sh"

pushd "$MYTMPDIR" &> /dev/null

bash exaslct_install_template.sh --help