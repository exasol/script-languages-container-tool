#!/bin/bash

set -u

interesting_paths=("scripts" "exasol_script_languages_container_tool/starter_scripts" "githooks" "docker_runner" "project_management_scripts")

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
status=0

for path in "${interesting_paths[@]}"; do
  find "$SCRIPT_DIR/../../$path" -name '*.sh' -type f -print0 | xargs -0 -n1 shellcheck -x
  test $? -ne 0 && status=1
done

exit "$status"