#!/bin/bash

# this script is for running linting and tests
# make sure you have all the dependencies installed first

set -e # exit immediately if a command fails

# function to run linting
run_lint() {
    echo "running linters..."
    flake8 src/ tests/ # checking python code style
    black --check src/ tests/ # checking code formatting
}

# function to run tests
run_tests() {
    echo "running tests..."
    pytest tests/ # running tests with pytest
}

# main function to control the script flow
main() {
    echo "starting dev tools script"
    run_lint
    run_tests
    echo "all checks passed"
}

# execute the main function
main

# TODO: consider adding options for docker and local run in the future