#!/usr/bin/env bash

set -e

cd "$1"

echo "************* RUN BASH TEST **********"
./scripts/test/test_starter_scripts.sh
echo "************* FINISHED BASH TEST *****"

#Force to rebuild exaslct docker image. Thus we avoid using a cached docker image (which is based on git sha)
export EXASLCT_FORCE_REBUILD=1

./exaslct --help
./exaslct export --flavor-path ./test/resources/flavors/test-flavor --export-path ./out
./exaslct export --flavor-path "./test/resources/flavors/test-flavor spaces/real-test-flavor" --export-path ./out
