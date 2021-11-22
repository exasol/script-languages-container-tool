#!/bin/bash
  
SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

source "$SCRIPT_DIR/../../starter_scripts/poetry_utils.sh"

check_requirements

set -euo pipefail

init_poetry

#Force to rebuild exaslct docker image. Thus we avoid using a cached docker image (which is based on git sha)
export EXASLCT_FORCE_REBUILD=1

if [[ $1 == "--no-rebuild" ]]; then
  unset EXASLCT_FORCE_REBUILD
  shift 1
fi

if [ -n "$POETRY_BIN" ]
then
  PYTHONPATH=. $POETRY_BIN run python3 "${@}"
else
  echo "Could not find poetry!"
  exit 1
fi

