# Script-Languages-Container-Tool 0.1.0, released 2021-06-16

Code name: Extraction from Script-Languages Repository

## Features / Enhancements

- #1: Add initial version
- #3: Add installer scripts which download and install the scripts to run exaslct from a prebuild docker container
- #19: Forward the docker registry password environment variables to the docker runner
- #10: Improve exaslct starter script to mount all path which are used by the command line parameter
- #33: Integrate integration-test-environment to version 0.3.1

## Bug Fixes

- #6: Fix docker repository name in construct_docker_runner_image_name.sh
- #8: Fix call to construct_docker_runner_image_name.sh in push_docker_runner_image.sh
- #12: Change the default for install_or_update_exaslct.sh to latest
- #17: Make default value for EXASLCT_INSTALL_DIRECTORY in installer a relative path
- #22: Fix overwriting env-file for the container in the docker starter and fix the umask
- #25: Write standard out/err to log file in the job directory to log file
- #26: Using host network for execution of exasclt
- #34: Fix docker image labels for merges to main and for releases

## Documentation

- #9: Add, fix and organize documentation
- #40: Update changelog for v0.1.0
