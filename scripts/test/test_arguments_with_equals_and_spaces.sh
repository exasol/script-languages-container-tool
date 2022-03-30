#!/usr/bin/env bash

#set -e => immediately exit if any command [1] has a non-zero exit status
#set -u => reference to any variable you haven't previously defined is an error and causes the program to immediately exit.
#set -o pipefailt => This setting prevents errors in a pipeline from being masked.
#                    If any command in a pipeline fails,
#                    that return code will be used as the return code of the whole pipeline.

if [[ -n "$TEST_DEBUG_OPTIONS" ]]; then
  set $TEST_DEBUG_OPTIONS
fi

set -euo pipefail

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"/
PROJECT_ROOT_DIR="$SCRIPT_DIR/../.."
STARTER_SCRIPT_DIR="$PROJECT_ROOT_DIR/exasol_script_languages_container_tool/starter_scripts"

source "$SCRIPT_DIR/assert.sh"
source "$STARTER_SCRIPT_DIR/mount_point_parsing.sh"

echo "Test arguments with = and spaces"
flavorDirB="$SCRIPT_DIR/abc def"

mkdir "$flavorDirB" || true
trap 'rm -rf "$flavorDirB"' EXIT
trap 'rm -rf "$flavorDirB"' ERR

testStr=$(print_mount_point_paths "--flavor-path=$flavorDirB")

assert "$testStr" "$flavorDirB "
