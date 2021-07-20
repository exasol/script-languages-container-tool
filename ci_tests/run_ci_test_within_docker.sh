#!/usr/bin/env bash

set -e

cd $1

echo "************* RUN BASH TEST **********"
./starter_scripts/test/test_scripts.sh
echo "************* FINISHED BASH TEST *****"

./exaslct export --flavor-path ./test/resources/test-flavor --export-path ./out