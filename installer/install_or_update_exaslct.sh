#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

die() { echo "$*" 1>&2 ; exit 1; }

if [ -z "${1-}" ]
then
  SLCT_GIT_REF="main"
else
  SLCT_GIT_REF="$1"
fi

DOWNLOAD_URL="https://raw.githubusercontent.com/exasol/script-languages-container-tool/$SLCT_GIT_REF/installer/"

TMP_DIRECTORY_FOR_INSTALLER="$(mktemp -d)"
trap 'rm -rf -- "$TMP_DIRECTORY_FOR_INSTALLER"' EXIT

INSTALLER_FILE_NAME="exaslct_installer.sh"
INSTALLER_CHECKSUM_FILE_NAME="exaslct_installer.sh.sha512sum"

pushd $TMP_DIRECTORY_FOR_INSTALLER &> /dev/null

curl -s -L "$DOWNLOAD_URL/$INSTALLER_FILE_NAME" -o "$INSTALLER_FILE_NAME" \
 || die "ERROR: Could not download the installer."
curl -s -L "$DOWNLOAD_URL/checksums/$INSTALLER_CHECKSUM_FILE_NAME" -o "$INSTALLER_CHECKSUM_FILE_NAME" \
 || die "ERROR: Could not download the checksum of the installer."
sha512sum --check "$INSTALLER_CHECKSUM_FILE_NAME" \
 || die "ERROR: Could not verify the checksum of the installer."

echo "test"

popd &> /dev/null

bash "$TMP_DIRECTORY_FOR_INSTALLER/$INSTALLER_FILE_NAME"
