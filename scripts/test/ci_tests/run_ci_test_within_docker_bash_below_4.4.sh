#!/usr/bin/env bash

set -e

cd "$1"

echo "************* RUN BASH TEST **********"
./scripts/test/test_starter_scripts.sh
echo "************* FINISHED BASH TEST *****"

#Force to rebuild exaslct docker image. Thus we avoid using a cached docker image (which is based on git sha)
export EXASCLCT_FORCE_REBUILD=1

./exaslct --help
./exaslct export --flavor-path ./test/resources/test-flavor --export-path ./out
./exaslct export --flavor-path "./test/resources/test-flavor spaces/real-test-flavor" --export-path ./out || (echo "spaces_failed" > "/tmp/spaces_failed")

if [[ ! -e "/tmp/spaces_failed" ]]; then
  echo "Test with spaces didn't failed. This is not expected for bash 4.4- (${BASH_VERSION})"
  exit 1
fi
