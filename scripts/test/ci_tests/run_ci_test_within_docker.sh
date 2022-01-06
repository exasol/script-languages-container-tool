#!/usr/bin/env bash

set -e

cd "$1"

echo "************* RUN BASH TEST **********"
./starter_scripts/test/test_scripts.sh
echo "************* FINISHED BASH TEST *****"

#Force to rebuild exaslct docker image. Thus we avoid using a cached docker image (which is based on git sha)
export EXASCLCT_FORCE_REBUILD=1

./exaslct export --flavor-path ./test/resources/test-flavor --export-path ./out