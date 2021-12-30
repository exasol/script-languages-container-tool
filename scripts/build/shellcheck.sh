#!/bin/bash

set -euo pipefail

interesting_paths=("scripts" "starter_scripts" "githooks" "installer" "project_management_scripts")

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

for path in "${interesting_paths[@]}"; do
  find "$SCRIPT_DIR/../../$path" -name '*.sh' -type f -print0 | xargs -0 -n1 shellcheck -x
done
