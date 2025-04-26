#!/bin/bash
# This script runs Ruff for linting and formatting

# Run Ruff to check and fix issues
echo "Running Ruff to check and fix issues"
output="$(ruff check . --fix)"
exit_code=$?

if [[ $exit_code -eq 0 ]]
then
    printf "Ruff completed successfully. No issues found or all issues were auto-fixed.\n"
elif [[ $exit_code -eq 1 ]]
then
    printf "Ruff found issues that couldn't be auto-fixed:\n"
    printf "%s\n" "$output"
    exit 1
else
    printf "Ruff encountered an error:\n"
    printf "%s\n" "$output"
    exit $exit_code
fi