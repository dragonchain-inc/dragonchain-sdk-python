#!/usr/bin/env sh

# Makes sure we're in this script's directory
cd $(dirname "$(readlink -f "$0")")

USAGE="usage: run.sh [command]

command
unit         : run unit tests on the project
integration  : run integration tests on the project
tests        : run all tests on the project
coverage     : run the coverage report (only works after tests have been run)
clean        : remove compiled python/other build/distrubition artifacts from the local project
linter       : run the flake8 linter against the project
build        : build the project from source
install      : install the project from source (depends on running build first)
build-dist   : build the distribution artifcats for the project from source
dist-release : upload and distribute the artifacts from build-dist to pypi
install-req  : install the python dependencies to dev on the project"

if [ $# -ne 1 ]; then
    echo "$USAGE"
elif [ "$1" = "unit" ]; then
    coverage run -m unittest tests/unit/*tests.py
elif [ "$1" = "integration" ]; then
    coverage run -m unittest tests/integration/*tests.py
elif [ "$1" = "tests" ]; then
    coverage run -m unittest tests/*/*tests.py
elif [ "$1" = "coverage" ]; then
    coverage report -m --include=$(find ./dc_sdk/ | tr '\n' ',' | rev | cut -c 2- | rev)
elif [ "$1" = "clean" ]; then
    rm -rf $(find . -name *.pyc) $(find . -name __pycache__) .coverage build/ dist/ dc_sdk.egg-info/
elif [ "$1" = "linter" ]; then
    flake8 $(find . -name \*.py)
elif [ "$1" = "build" ]; then
    python3 setup.py build
elif [ "$1" = "install" ]; then
    python3 setup.py install
elif [ "$1" = "build-dist" ]; then
    python3 setup.py sdist bdist_wheel
elif [ "$1" = "dist-release" ]; then
    twine upload dist/*
elif [ "$1" = "install-req" ]; then
    python3 -m pip install -r requirements.txt --user
else
    echo "$USAGE"
fi
