#!/usr/bin/env sh
set -e
# Makes sure we're in this script's directory
cd "$(dirname "$(readlink -f "$0")")"

USAGE="usage: run.sh [command]

command
unit         : run unit tests on the project
integration  : run integration tests on the project
tests        : run all tests on the project
coverage     : run the coverage report (only works after tests have been run)
linter       : run the flake8 linter against the project
bandit       : run security linting with bandit against the project
build        : build the project from source
install      : install the project from source (depends on running build first)
install-req  : install the python dependencies to dev on the project
build-dist   : build the distribution artifcats for the project from source
dist-release : upload and distribute the artifacts from build-dist to pypi
clean        : remove compiled python/other build/distrubition artifacts from the local project"

if [ $# -ne 1 ]; then
    echo "$USAGE"
    exit 1
elif [ "$1" = "unit" ]; then
    python3 -m coverage run --branch -m unittest tests/unit/*tests.py
elif [ "$1" = "integration" ]; then
    python3 -m coverage run -m unittest tests/integration/*tests.py
elif [ "$1" = "tests" ]; then
    python3 -m coverage run --branch -m unittest tests/*/*tests.py
elif [ "$1" = "coverage" ]; then
    python3 -m coverage report -m --include=$(find ./dc_sdk/ | tr '\n' ',' | rev | cut -c 2- | rev)
elif [ "$1" = "linter" ]; then
    python3 -m flake8 $(find . -name \*.py)
elif [ "$1" = "bandit" ]; then
    python3 -m bandit -r .
elif [ "$1" = "build" ]; then
    python3 setup.py build
elif [ "$1" = "install" ]; then
    python3 setup.py install
elif [ "$1" = "install-req" ]; then
    python3 -m pip install -r requirements.txt --user
elif [ "$1" = "build-dist" ]; then
    python3 setup.py sdist bdist_wheel
elif [ "$1" = "dist-release" ]; then
    python3 -m twine upload dist/*
elif [ "$1" = "clean" ]; then
    rm -rfv $(find . -name *.pyc) $(find . -name __pycache__) tests/unit/dragonchain/ .coverage build/ dist/ dc_sdk.egg-info/
else
    echo "$USAGE"
    exit 1
fi
