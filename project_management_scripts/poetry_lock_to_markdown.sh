#!/usr/bin/env bash

set -euo pipefail

poetry export -f requirements.txt --without-hashes --with-credentials | cut -f1 -d ";" | sed "s/==/|/g" | sed -E "s/^(.*)$/|\1|/g"