#!/bin/bash

# this script sets up the development environment for linting and testing

set -e  # exit immediately if a command exits with a non-zero status

# check if required tools are installed
function check_tools() {
    for tool in pylint pytest; do
        if ! command -v $tool &> /dev/null; then
            echo "$tool could not be found, please install it"
            exit 1
        fi
    done
}

# lint the python files
function lint_code() {
    echo "running linter..."
    pylint src/  # linter for source code
}

# run the tests
function run_tests() {
    echo "running tests..."
    pytest tests/  # run tests in the tests directory
}

# main function to orchestrate the tasks
function main() {
    check_tools
    lint_code
    run_tests
    echo "all checks passed!"
}

# run the main function
main

# TODO: add docker support for running tests in a container if needed