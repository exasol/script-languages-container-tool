#!/usr/bin/env bash

#set -e => immediately exit if any command [1] has a non-zero exit status
#set -u => reference to any variable you haven't previously defined is an error and causes the program to immediately exit.
#set -o pipefail => This setting prevents errors in a pipeline from being masked.
#                    If any command in a pipeline fails,
#                    that return code will be used as the return code of the whole pipeline.
set -euo pipefail


SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

echo "Running test_exaslct_install_template_with_current_ref.sh"
bash "$SCRIPT_DIR/test_exaslct_install_template_with_current_ref.sh"
echo
echo "====================================================================="
echo

echo "Running test_install_or_update_exaslct_with_current_ref_default_environment.sh"
bash "$SCRIPT_DIR/test_install_or_update_exaslct_with_current_ref_default_environment.sh"
echo
echo "====================================================================="
echo