#!/usr/bin/env bash

set -euo pipefail

die() {
  echo "$*" 1>&2
  exit 1
}
download_raw_file_from_github() {
  local repo=$1
  local ref=$2
  local remote_file_path=$3
  local local_file_path=$4
  local url="https://api.github.com/repos/$repo/contents/$remote_file_path?ref=$ref"
  local arguments=(-s -H 'Accept: application/vnd.github.v3.raw' -L "$url" -o "$local_file_path")
  if [ -z "${GITHUB_TOKEN-}" ]; then
    curl "${arguments[@]}"
  else
    curl -H "Authorization: token $GITHUB_TOKEN" "${arguments[@]}"
  fi
}
download_and_verify_raw_file_from_github() {
  local repo=$1
  local ref=$2
  local remote_file_path=$3
  local file_name=${remote_file_path##*/}
  local dir_path=${remote_file_path%$file_name}
  local checksum_file_name="${file_name}.sha512sum"
  local remote_checksum_file_path="${dir_path}checksums/$checksum_file_name"

  download_raw_file_from_github "$repo" "$ref" "$remote_file_path" "$file_name" ||
    die "ERROR: Could not download '$remote_file_path' from the github repository '$repo' at ref '$ref'."
  download_raw_file_from_github "$repo" "$ref" "$remote_checksum_file_path" "$checksum_file_name" ||
    die "ERROR: Could not download the checksum for '$remote_file_path' from the github repository '$repo' at ref '$ref'."
  sha512sum --check "${checksum_file_name}" ||
    die "ERROR: Could not verify the checksum for '$remote_file_path' from the github repository '$repo' at ref '$ref'."
}

main() {
  local exaslct_git_ref="$1"
  local repo="exasol/script-languages-container-tool"

  if [ -z "${EXASLCT_INSTALL_DIRECTORY-}" ]; then
    EXASLCT_INSTALL_DIRECTORY=$PWD/exaslct_scripts
  fi

  if [ -e "$EXASLCT_INSTALL_DIRECTORY" ]; then
    echo "The installation directory for exaslct at '$EXASLCT_INSTALL_DIRECTORY' already exists."
    echo "Do you want to remove it and continue with installation?"
    echo -n "yes/no: "
    local answer
    read -r answer
    if [ "$answer" == "yes" ]; then
      rm -r "$EXASLCT_INSTALL_DIRECTORY"
    else
      echo "Can't continue with the installation, because the installation directory already exists."
      echo "You can change the installation directory by setting the environment variable EXASLCT_INSTALL_DIRECTORY"
      exit 1
    fi
  fi

  mkdir "$EXASLCT_INSTALL_DIRECTORY"
  pushd "$EXASLCT_INSTALL_DIRECTORY"

  download_and_verify_raw_file_from_github "$repo" "$exaslct_git_ref" "starter_scripts/exaslct_within_docker_container_without_container_build.sh"
  download_and_verify_raw_file_from_github "$repo" "$exaslct_git_ref" "starter_scripts/exaslct_within_docker_container.sh"
  download_and_verify_raw_file_from_github "$repo" "$exaslct_git_ref" "starter_scripts/construct_docker_runner_image_name.sh"
  download_and_verify_raw_file_from_github "$repo" "$exaslct_git_ref" "installer/exaslct_install_template.sh"

  mv exaslct_install_template.sh exaslct.sh

  sed -i "s/<<<<EXASLCT_GIT_REF>>>>/$exaslct_git_ref/g" exaslct.sh

  popd

  if [ -z "${EXASLCT_SYM_LINK_PATH-}" ]; then
    EXASLCT_SYM_LINK_PATH=$PWD/exaslct
  fi

  if [ -e "$EXASLCT_SYM_LINK_PATH" ]; then
    echo "The path for the symlink to exaslct at '$EXASLCT_SYM_LINK_PATH' already exists."
    echo "Do you want to remove it and continue with installation?"
    echo -n "yes/no: "
    local answer
    read -r answer
    if [ "$answer" == "yes" ]; then
      rm -r "$EXASLCT_SYM_LINK_PATH"
    else
      echo "Can't continue with the installation, because the path to exaslct symlink already exists."
      echo "You can change the path to exaslct symlink by setting the environment variable EXASLCT_SYM_LINK_PATH"
      exit 1
    fi
  fi
  ln -s "$EXASLCT_INSTALL_DIRECTORY/exaslct.sh" "$EXASLCT_SYM_LINK_PATH"
}

main "${@}"
