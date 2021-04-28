#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

if [ -z "${1-}" ]
then
  VERSION="$(git rev-parse HEAD 2> /dev/null || echo latest)"
else
  VERSION="$1"
fi

echo "exasol/script-languages:container-tool-runner-$VERSION"
