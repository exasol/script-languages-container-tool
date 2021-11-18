#!/usr/bin/env bash

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

declare -a test_array=( $(ls $SCRIPT_DIR/../../test/test_*.py))
printf '%s\n' "${test_array[@]}" | jq -R . | jq -cs .