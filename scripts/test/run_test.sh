#!/bin/bash

set -euo pipefail

#Force to rebuild exaslct docker image. Thus we avoid using a cached docker image (which is based on git sha)
export EXASLCT_FORCE_REBUILD=1

if [[ $1 == "--no-rebuild" ]]; then
  unset EXASLCT_FORCE_REBUILD
  shift 1
fi

poetry run python3 "${@}"
