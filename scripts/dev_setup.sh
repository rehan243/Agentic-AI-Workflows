#!/bin/bash

# this script sets up the development environment and runs tests

# check if docker is running
if ! docker info > /dev/null 2>&1; then
  echo "docker is not running. please start docker and try again"
  exit 1
fi

# pull the latest images
echo "pulling latest docker images"
docker-compose pull

# build the project
echo "building the project"
docker-compose build

# run linting
echo "running linters"
docker-compose run --rm app flake8 src/

# run tests
echo "running tests"
docker-compose run --rm app pytest tests/

# check for any remaining containers
if [ "$(docker ps -q)" ]; then
  echo "some containers are still running. please check them"
else
  echo "all containers stopped successfully"
fi

# cleanup unused docker resources
echo "cleaning up unused docker resources"
docker system prune -f

echo "development setup and tests completed"