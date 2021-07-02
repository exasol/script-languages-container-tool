#!/usr/bin/env bash

set -e

CI_ENVS=("CentOs7" "CentOs8" "Ubuntu18.04" "Ubuntu20.04")
printf '%s\n' ${CI_ENVS[@]} | jq -R . | jq -cs .