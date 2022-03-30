#!/usr/bin/env bash

#set -e => immediately exit if any command [1] has a non-zero exit status
#set -u => reference to any variable you haven't previously defined is an error and causes the program to immediately exit.
#set -o pipefailt => This setting prevents errors in a pipeline from being masked.
#                    If any command in a pipeline fails,
#                    that return code will be used as the return code of the whole pipeline.
set -euo pipefail

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
bash "$SCRIPT_DIR/test_arguments_with_equals.sh"
bash "$SCRIPT_DIR/test_arguments_with_spaces.sh"
bash "$SCRIPT_DIR/test_arguments_with_equals_and_spaces.sh"
