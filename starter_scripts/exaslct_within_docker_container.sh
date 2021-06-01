#!/usr/bin/env bash

#set -e => immediately exit if any command [1] has a non-zero exit status
#set -u => reference to any variable you haven't previously defined is an error and causes the program to immediately exit.
#set -o pipefailt => This setting prevents errors in a pipeline from being masked.
#                    If any command in a pipeline fails,
#                    that return code will be used as the return code of the whole pipeline.
set -euo pipefail

RUNNER_IMAGE_NAME="$1"
shift 1

if [[ -t 1 ]]; then
  terminal_parameter=-it
else
  terminal_parameter=""
fi


relevant_mount_point_arguments=("--flavor-path" "--export-path" "--output-directory" "--temporary-base-directory"
                                "--cache-directory" "--save-directory" "--task-dependencies-dot-file" "--test-folder"
                                "--test-file" "--temporary-base-directory")

function _get_mount_point_argument() {
  current_arg=$1
  next_arg=$2
#  temp="${next_arg%\"}" NEED TO CHECK IF I NEED ARGUMENTS WITH/WITHOUT QUOTES
#  temp="${temp#\"}"
  if [ -d  $next_arg ]; then
    mount_point_arguments+=$next_arg
  elif [ -f $next_arg ]; then
    mount_point_arguments+="$(dirname "${next_arg}")"
  else
    echo "Invalid argument for $current_arg: $next_arg needs to be a directory"
    exit -1
  fi
}

function _get_mount_point_arguments() {
  lenArgs="$#"
  retVal=()
  echo "Len Args: $lenArgs"
  for ((idxArg=1; idxArg < $lenArgs; idxArg++))
    do
    current_arg=${!idxArg}
    next_arg_idx=$((idxArg+1))
    next_arg=${!next_arg_idx}
    echo "Check $current_arg"
    if [[ " ${relevant_mount_point_arguments[@]} " =~ " ${current_arg} " ]]; then
      echo "Found:$next_arg"
      _get_mount_point_argument $current_arg $next_arg
    fi
    done
}

mount_point_arguments=''
_get_mount_point_arguments ${@}
echo "MountPoint args:$mount_point_arguments"


quoted_arguments=''
for argument in "${@}"; do
  argument="${argument//\\/\\\\}"
  quoted_arguments="$quoted_arguments \"${argument//\"/\\\"}\""
done

###now collect list of mount points based on valid_mount_point_arguments....

RUN_COMMAND="/script-languages-container-tool/starter_scripts/exaslct_without_poetry.sh $quoted_arguments; RETURN_CODE=\$?; chown -R $(id -u):$(id -g) .build_output &> /dev/null; exit \$RETURN_CODE"

HOST_DOCKER_SOCKER_PATH="/var/run/docker.sock"
CONTAINER_DOCKER_SOCKER_PATH="/var/run/docker.sock"
DOCKER_SOCKET_MOUNT="$HOST_DOCKER_SOCKER_PATH:$CONTAINER_DOCKER_SOCKER_PATH"

function create_env_file() {
  touch "$tmpfile_env"
  if [ -n "${TARGET_DOCKER_PASSWORD-}" ]; then
    echo "TARGET_DOCKER_PASSWORD=$TARGET_DOCKER_PASSWORD" >> "$tmpfile_env"
  fi
  if [ -n "${SOURCE_DOCKER_PASSWORD-}" ]; then
    echo "SOURCE_DOCKER_PASSWORD=$SOURCE_DOCKER_PASSWORD" >> "$tmpfile_env"
  fi
}

function create_env_file_debug_protected() {
  shell_options="$-"
  case $shell_options in
  *x*) set +x ;;
  *) echo &>/dev/null ;;
  esac

  create_env_file "$1"

  case $shell_options in
  *x*) set -x ;;
  *) echo &>/dev/null ;;
  esac
}

old_umask=$(umask)
umask 277
tmpfile_env=$(mktemp)
trap 'rm -f -- "$tmpfile_env"' INT TERM HUP EXIT

create_env_file_debug_protected "$tmpfile_env"

docker run --env-file "$tmpfile_env" --rm $terminal_parameter -v "$PWD:$PWD" -v "$DOCKER_SOCKET_MOUNT" "$mount_point_arguments" -w "$PWD" "$RUNNER_IMAGE_NAME" bash -c "$RUN_COMMAND"

umask "$old_umask"
