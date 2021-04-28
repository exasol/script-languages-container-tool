#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

SLCT_GIT_REF="$1"

GIT_RAW_URL="https://raw.githubusercontent.com/exasol/script-languages-container-tool/$SLCT_GIT_REF/"

if [ -z "${EXASLCT_INSTALL_DIRECTORY-}" ]
then
  EXASLCT_INSTALL_DIRECTORY=$PWD/exaslct_scripts
fi

if [ -e "$EXASLCT_INSTALL_DIRECTORY" ]
then
  echo "The installation directory for exaslct at '$EXASLCT_INSTALL_DIRECTORY' already exists."
  echo "Do you want to remove it and continue with installation?"
  echo -n "yes/no: "
  read ANSWER
  if [ "$ANSWER" == "yes" ]
  then
    rm -r "$EXASLCT_INSTALL_DIRECTORY"
  else
    echo "Can't continue with the installation, because the installation directory already exists."
    echo "You can change the installation directory by setting the environment variable EXASLCT_INSTALL_DIRECTORY"
    exit 1
  fi
fi

mkdir "$EXASLCT_INSTALL_DIRECTORY"
pushd "$EXASLCT_INSTALL_DIRECTORY"

curl -L "$GIT_RAW_URL/exaslct-within-docker-container" -o "exaslct-within-docker-container"
curl -L "$GIT_RAW_URL/installer/exaslct-install-template.sh" -o "exaslct"
curl -L "$GIT_RAW_URL/construct_docker_runner_image_name.sh" -o "construct_docker_runner_image_name.sh"

sed "s/<<<<RUNNER_IMAGE_NAME>>>>/$SLCT_GIT_REF/g" exaslct

popd

if [ -z "${$EXASLCT_SYM_LINK_PATH-}" ]
then
  EXASLCT_SYM_LINK_PATH=$PWD/exaslct
fi

if [ -e "exaslct" ]
then
  echo "The path for the symlink to exaslct at '$EXASLCT_SYM_LINK_PATH' already exists."
  echo "Do you want to remove it and continue with installation?"
  echo -n "yes/no: "
  read ANSWER
  if [ "$ANSWER" == "yes" ]
  then
    rm -r "$EXASLCT_SYM_LINK_PATH"
  else
    echo "Can't continue with the installation, because the path to exaslct symlink already exists."
    echo "You can change the path to exaslct symlink by setting the environment variable EXASLCT_SYM_LINK_PATH"
    exit 1
  fi
fi
ln -s "$EXASLCT_INSTALL_DIRECTORY/exaslct" "$EXASLCT_SYM_LINK_PATH"