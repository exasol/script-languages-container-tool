#!/usr/bin/env bash

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

# Ignore shellcheck rule SC2207 here: Alternatives are difficult to read and understand. None of the test filename has spaces or globs, so it's safe.
# Ignore shellcheck rule SC2086 here: ls does not work correct with quotes here (probably because of the asterisk).
# shellcheck disable=SC2207,SC2086
declare -a test_array=( $(ls $SCRIPT_DIR/../../test/test_*.py))
printf '%s\n' "${test_array[@]}" | jq -R . | jq -cs .