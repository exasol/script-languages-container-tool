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

declare -A relevant_mount_point_arguments
relevant_mount_point_arguments["--flavor-path"]=in_path
relevant_mount_point_arguments["--export-path"]=out_path
relevant_mount_point_arguments["--output-directory"]=out_path
relevant_mount_point_arguments["--temporary-base-directory"]=out_path
relevant_mount_point_arguments["--cache-directory"]=in_path
relevant_mount_point_arguments["--save-directory"]=out_path
relevant_mount_point_arguments["--task-dependencies-dot-file"]=out_file
relevant_mount_point_arguments["--test-folder"]=in_path
relevant_mount_point_arguments["--test-file"]=in_file

function _get_mount_point_docker_arg() {
  mount_point_path=

}

function _get_mount_point_argument() {
  current_arg=$1
  next_arg=$2
  arg_type=$3
  #  temp="${next_arg%\"}" NEED TO CHECK IF I NEED ARGUMENTS WITH/WITHOUT QUOTES
  #  temp="${temp#\"}"
  case $arg_type in
  in_path)
    if [[ -d $next_arg ]]; then
      mount_point_arguments+=("$next_arg")
    else
      echo "Input directory $next_arg for parameter $current_arg does not exist."
      exit 1
    fi
    ;;
  in_file)
    if [[ -f $next_arg ]]; then
      local rel_dir_name="$(dirname "${next_arg}")"
      mount_point_arguments+=("$rel_dir_name")
    else
      echo "Input file $next_arg for parameter $current_arg does not exist."
      exit 1
    fi
    ;;
  out_path)
    #Create out directories if necessary
    if [[ ! -d $next_arg ]]; then
      mkdir -p "$next_arg"
    fi
    mount_point_arguments+=("$next_arg")
    ;;
  out_file)
    local rel_dir_name="$(dirname "${next_arg}")"
    #Create out directories if necessary
    if [[ ! -d $next_arg ]]; then
      mkdir -p "$rel_dir_name"
    fi
    mount_point_arguments+=("$rel_dir_name")
    ;;
  *)
    echo "INVALID ARGUMENT. Please adjust variable relevant_mount_point_arguments in $0!"
    exit 1
    ;;
  esac
}

function _get_mount_point_arguments() {
  lenArgs="$#"
  for ((idxArg = 1; idxArg < $lenArgs; idxArg++)); do
    current_arg=${!idxArg}
    next_arg_idx=$((idxArg + 1))
    next_arg=${!next_arg_idx}
    if [ -v relevant_mount_point_arguments[$current_arg] ]; then
      _get_mount_point_argument $current_arg $next_arg ${relevant_mount_point_arguments[$current_arg]}
    fi
  done
}

declare -a mount_point_arguments
_get_mount_point_arguments ${@}

quoted_arguments=''
for argument in "${@}"; do
  argument="${argument//\\/\\\\}"
  quoted_arguments="$quoted_arguments \"${argument//\"/\\\"}\""
done

chown_parameter=${mount_point_arguments[@]}

echo "chown_parameter:$chown_parameter"

mount_point_parameter=''
for i in "${mount_point_arguments[@]}"; do
  mount_point_argument=mount_point_arguments[i]
  host_dir_name=$(readlink -f "${mount_point_argument}")
  container_dir_name=$(realpath -s "${mount_point_argument}")
  mount_point_parameter="$mount_point_parameter-v ${host_dir_name}:${container_dir_name} "
done

RUN_COMMAND="/script-languages-container-tool/starter_scripts/exaslct_without_poetry.sh $quoted_arguments; RETURN_CODE=\$?; chown -R $(id -u):$(id -g) .build_output chown_parameter &> /dev/null; exit \$RETURN_CODE"

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
docker run --env-file "$tmpfile_env" --rm $terminal_parameter -v "$PWD:$PWD" -v "$DOCKER_SOCKET_MOUNT" -w "$PWD" ${mount_point_parameter[@]} "$RUNNER_IMAGE_NAME" bash -c "$RUN_COMMAND"

umask "$old_umask"
