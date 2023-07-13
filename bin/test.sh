#!/usr/bin/env bash
##
# Run tests in CI.
#
set -e

echo "==> Lint code"
ahoy lint

ahoy test-unit

ahoy install-site
ahoy test-bdd
