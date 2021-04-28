#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

echo "Running test_exaslct_install_template_with_current_ref.sh"
bash "$SCRIPT_DIR/test_exaslct_install_template_with_current_ref.sh"

echo "Running test_install_or_update_exaslct_with_current_ref_default_environment.sh"
bash "$SCRIPT_DIR/test_install_or_update_exaslct_with_current_ref_default_environment.sh"


