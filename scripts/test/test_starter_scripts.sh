#!/usr/bin/env bash

#set -e => immediately exit if any command [1] has a non-zero exit status
#set -u => reference to any variable you haven't previously defined is an error and causes the program to immediately exit.
#set -o pipefailt => This setting prevents errors in a pipeline from being masked.
#                    If any command in a pipeline fails,
#                    that return code will be used as the return code of the whole pipeline.
set -euo pipefail

SCRIPT_DIR="$(dirname "$($rl -f "${BASH_SOURCE[0]}")")"
PROJECT_ROOT_DIR="$SCRIPT_DIR/../.."
STARTER_SCRIPT_DIR="$PROJECT_ROOT_DIR/exasol_script_languages_container_tool/starter_scripts"


function assert() {
  cmpA=$1
  shift 1
  cmpB="${*}"
  if [[ $cmpA != "$cmpB" ]]; then
    >&2 echo "ERROR: '$cmpA' does not match'$cmpB'"
    exit 1
  fi
}

flavorDirA="$SCRIPT_DIR/test/abc=def"
exportDirA="$SCRIPT_DIR/test/exportdir=xyz"

mkdir "$flavorDirA" || true
trap 'rm -rf "$flavorDirA" "$exportDirA"' EXIT

testStr=$(bash "$STARTER_SCRIPT_DIR/mount_point_parsing.sh" --flavor-path="$flavorDirA" --export-path "$exportDirA" dummy)

assert "$testStr" "$flavorDirA" "$exportDirA" "" #Last element ist dummy element
