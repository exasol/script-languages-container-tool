#!/bin/bash 
   

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" 

#shellcheck source=./starter_scripts/poetry_utils.sh
source "$SCRIPT_DIR/../../starter_scripts/poetry_utils.sh"

check_requirements

set -euo pipefail

init_poetry

if [ -n "$POETRY_BIN" ]
then
  PYTHONPATH=. $POETRY_BIN build
else
  echo "Could not find poetry!"
  exit 1
fi

