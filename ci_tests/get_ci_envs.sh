#!/usr/bin/env bash

set -e

CI_ENVS=("CentOs7")
printf '%s\n' ${CI_ENVS[@]} | jq -R . | jq -cs .