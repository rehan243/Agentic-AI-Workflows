#!/bin/bash

# this script sets up the development environment for the project

set -e  # exit immediately if a command exits with a non-zero status

# check for required commands
if ! command -v python3 &> /dev/null; then
    echo "python3 is not installed, please install it first"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed, please install it first"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "docker is not installed, please install it first"
    exit 1
fi

# create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "creating a virtual environment"
    python3 -m venv venv
fi

# activate the virtual environment
source venv/bin/activate

# install requirements
echo "installing requirements"
pip3 install -r requirements.txt

# run linters
echo "running linters"
flake8 src/  # TODO: add more linters if needed

# run tests
echo "running tests"
pytest tests/  # TODO: ensure coverage checks are in place

# build and run docker container
echo "building and running docker container"
docker-compose up --build -d

echo "development environment set up complete"