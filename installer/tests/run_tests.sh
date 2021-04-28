#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

echo "Running test_installer_current_ref_default_environment.sh"
bash "$SCRIPT_DIR/test_installer_current_ref_default_environment.sh"


