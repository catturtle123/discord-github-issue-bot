#!/bin/bash
# Pre-commit hook: lint and format check
set -e

echo "Running ruff check..."
ruff check .

echo "Running ruff format check..."
ruff format . --check

echo "All checks passed!"
