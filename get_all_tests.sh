#!/usr/bin/env bash

declare -a test_array=( $(ls test/test_*.py))
printf '%s\n' "${test_array[@]}" | jq -R . | jq -cs .