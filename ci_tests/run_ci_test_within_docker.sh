#!/usr/bin/env bash

set -e

cd $1
./exaslct export --flavor-path ./test/resources/test-flavor --export-path ./out