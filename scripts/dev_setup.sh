#!/bin/bash

# this script sets up the development environment
# make sure you have all dependencies installed

# define some variables for easy reference
REPO_NAME="agentic-ai-workflows"
VENV_DIR=".venv"

# create a virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "creating virtual environment..."
    python3 -m venv $VENV_DIR
fi

# activate the virtual environment
source $VENV_DIR/bin/activate

# install dependencies
echo "installing dependencies..."
pip install -r requirements.txt

# run linting
echo "running flake8 for linting..."
flake8 src/

# run tests
echo "running tests with pytest..."
pytest tests/

# build docker image
echo "building docker image..."
docker build -t $REPO_NAME .

# cleanup
echo "cleaning up..."
deactivate

# TODO: maybe add a command to run the app locally

echo "development setup complete"