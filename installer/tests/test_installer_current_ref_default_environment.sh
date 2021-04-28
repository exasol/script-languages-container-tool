#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

INSTALLER_DIRECTORY="$SCRIPT_DIR/.."

MYTMPDIR="$(mktemp -d)"
trap 'rm -rf -- "$MYTMPDIR"' EXIT

GIT_REF=$(git rev-parse HEAD)

cp "$INSTALLER_DIRECTORY/install_or_update_exaslct.sh" "$MYTMPDIR/install_or_update_exaslct.sh"
pushd "$MYTMPDIR" &> /dev/null

bash install_or_update_exaslct.sh "$GIT_REF"
bash -x ./exaslct --help