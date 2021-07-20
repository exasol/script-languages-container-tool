#!/usr/bin/env bash

set -e

cd $1

./starter_scripts/test/test_scripts.sh

./exaslct export --flavor-path ./test/resources/test-flavor --export-path ./out