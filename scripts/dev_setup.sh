#!/bin/bash

# this script sets up the development environment for the project

# check if docker is running
if ! systemctl is-active --quiet docker; then
  echo "docker is not running. please start docker and try again"
  exit 1
fi

# create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo "creating a virtual environment"
  python3 -m venv venv
fi

# activate the virtual environment
source venv/bin/activate

# install dependencies
echo "installing dependencies"
pip install -r requirements.txt

# run linting
echo "running linting"
flake8 . || { echo "linting failed"; exit 1; }

# run tests
echo "running tests"
pytest tests/ || { echo "tests failed"; exit 1; }

# build docker image
echo "building docker image"
docker build -t agentic-ai-workflows . || { echo "docker build failed"; exit 1; }

# everything is good to go
echo "development environment is set up successfully"