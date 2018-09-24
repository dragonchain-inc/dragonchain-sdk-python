#!/usr/bin/env sh

# Makes sure we're in this script's directory
cd $(dirname "$(readlink -f "$0")")

USAGE="usage: run.sh [command]

command
unit     : run unit tests on the project
coverage : run the coverage report (only works after unit has been ran)
clean    : remove compile python from the local project
linter   : run the flake8 linter against the project
install  : install the python dependencies to run/dev the project"

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
    rm $(find . -name *.pyc) && rm -r $(find . -name __pycache__) && rm .coverage
elif [ "$1" = "linter" ]; then
    flake8 $(find . -name \*.py)
elif [ "$1" = "install" ]; then
    python3 -m pip install -r requirements.txt --user
else
    echo "$USAGE"
fi
