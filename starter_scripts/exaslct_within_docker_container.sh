#!/usr/bin/env bash

set -euo pipefail

RUNNER_IMAGE_NAME="$1"
shift 1

if [[ -t 1 ]]; then
  terminal_parameter=-it
else
  terminal_parameter=""
fi



build_mount_point_arguments=("--flavor-path" "--output-directory" "--temporary-base-directory"
                                "--cache-directory" "--task-dependencies-dot-file")
build_test_container_mount_point_arguments=("--temporary-base-directory" "--task-dependencies-dot-file")
clean_all_images_mount_point_arguments=("--output-directory" "--task-dependencies-dot-file")
clean_flavor_images_mount_point_arguments=("--flavor-path", "--output-directory", "--task-dependencies-dot-file")
export_mount_point_arguments=("--flavor-path" "--export-path " "--output-directory"
                                " --temporary-base-directory" "--cache-directory" "--task-dependencies-dot-file")
generate_language_activation_mount_point_arguments=("--flavor-path")
push_mount_point_arguments=("--flavor-path" "--output-directory" "--temporary-base-directory"
                              "--cache-directory" "--task-dependencies-dot-file")
push_test_container_mount_point_arguments=("--output-directory" "--temporary-base-directory"
                                "--cache-directory" "--task-dependencies-dot-file")
run_db_test_mount_point_arguments=("--flavor-path" " --test-folder" "--test-file"
                                      "--output-directory" "--temporary-base-directory"
                                      "--cache-directory" "--task-dependencies-dot-file")
save_mount_point_arguments=("--save-directory" "--flavor-path"  "--output-directory" "--temporary-base-directory"
                                      "--cache-directory" "--task-dependencies-dot-file")
spawn_test_environment_mount_point_arguments=("--output-directory" "--temporary-base-directory"
                                "--task-dependencies-dot-file")
upload_mount_point_arguments=("--flavor-path" "--output-directory" "--temporary-base-directory"
                                "--cache-directory" "--task-dependencies-dot-file")



declare -A cmd_related_mount_points
cmd_related_mount_points=( ["build"]=${build_mount_point_arguments[@]}
                                      ["build-test-container"]=${build_test_container_mount_point_arguments[@]}
                                      ["clean-all-images"]=${clean_all_images_mount_point_arguments[@]}
                                      ["clean-flavor-images"]=${clean_flavor_images_mount_point_arguments[@]}
                                      ["export"]=${export_mount_point_arguments[@]}
                                      ["generate-language-activation"]=${generate_language_activation_mount_point_arguments[@]}
                                      ["push"]=${push_mount_point_arguments[@]}
                                      ["push-test-container"]=${push_test_container_mount_point_arguments[@]}
                                      ["run-db-test"]=${run_db_test_mount_point_arguments[@]}
                                      ["save"]=${save_mount_point_arguments[@]}
                                      ["spawn-test-environment"]=${spawn_test_environment_mount_point_arguments[@]}
                                      ["upload"]=${upload_mount_point_arguments[@]})

echo "${cmd_related_mount_points['build']}"

base_cmd=$1

echo "base command: $base_cmd"

valid_mount_point_arguments=''
if [ -v cmd_related_mount_points[$base_cmd] ] ; then
  valid_mount_point_arguments=cmd_related_mount_points[$base_cmd]
  echo "Valid arguments:${cmd_related_mount_points[$base_cmd]}"
else
  echo "Invalid command"
  exit -1
fi



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

docker run --env-file "$tmpfile_env" --rm $terminal_parameter -v "$PWD:$PWD" -v "$DOCKER_SOCKET_MOUNT" -w "$PWD" "$RUNNER_IMAGE_NAME" bash -c "$RUN_COMMAND"

umask "$old_umask"
