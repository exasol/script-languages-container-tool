#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
# Ignore shellcheck rule here, as we want to split result by space
# shellcheck disable=SC2046
CI_ENVS=$(basename -a $(ls -d "${SCRIPT_DIR}"/*/))
printf '%s\n' "${CI_ENVS[@]}" | jq -R . | jq -cs .