#!/usr/bin/env bash

set -u


SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

returnValue=0

echo "Running test_exaslct_install_template_with_current_ref.sh"
bash "$SCRIPT_DIR/test_exaslct_install_template_with_current_ref.sh"
(( returnValue+=$? ))
echo
echo "====================================================================="
echo

echo "Running test_install_or_update_exaslct_with_current_ref_default_environment.sh"
bash "$SCRIPT_DIR/test_install_or_update_exaslct_with_current_ref_default_environment.sh"
(( returnValue+=$? ))
echo
echo "====================================================================="
echo
exit $returnValue