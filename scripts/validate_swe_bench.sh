#!/bin/bash

# SWE-bench Data Point Validator
# Validates SWE-bench data points using the official evaluation harness
# Usage: ./scripts/validate_swe_bench.sh [options]

set -e

# Change to the project root directory
cd "$(dirname "$0")/.."

# Use UV to run the Python module with all arguments passed through
uv run python -m swe_bench_validator "$@"
