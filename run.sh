#!/usr/bin/env sh
set -e
# Makes sure we're in this script's directory (avoid symlinks and escape special chars)
cd "$(cd "$(dirname "$0")"; pwd -P)"

USAGE="usage: run.sh [command]

command
unit         : run unit tests on the project
integration  : run integration tests on the project
coverage     : run the coverage report (only works after tests have been run)
tests        : run all tests on the project, including a unittest coverage report
linter       : run the flake8 linter against the project
bandit       : run security linting with bandit against the project
build        : build the project from source
docs         : generate the docs and place them into docs/.build
install      : install the project from source (depends on running build first)
install-req  : install the python dependencies to dev on the project
build-dist   : build the distribution artifcats for the project from source
clean        : remove compiled python/docs/other build or distrubition artifacts from the local project
pr-test      : run all of the tests that the pull request would check, locally
dist-release : upload and distribute the artifacts from build-dist to pypi"

if [ $# -ne 1 ]; then
    echo "$USAGE"
    exit 1
elif [ "$1" = "unit" ]; then
    python3 -m coverage run --branch -m unittest discover -s tests/unit -p "test_*.py"
elif [ "$1" = "integration" ]; then
    python3 -m unittest discover -s tests/integration -p "test_*.py"
elif [ "$1" = "tests" ]; then
    echo "Running unit tests"
    sh run.sh unit
    sh run.sh coverage
    echo "\nRunning integration tests"
    sh run.sh integration
elif [ "$1" = "coverage" ]; then
    python3 -m coverage report -m --include=$(find ./dragonchain_sdk/ | tr '\n' ',' | rev | cut -c 2- | rev)
elif [ "$1" = "linter" ]; then
    python3 -m flake8 $(find . -name \*.py)
elif [ "$1" = "bandit" ]; then
    python3 -m bandit -r .
elif [ "$1" = "build" ]; then
    python3 setup.py build
elif [ "$1" = "docs" ]; then
    cd docs
    make html
    cd ..
elif [ "$1" = "install" ]; then
    python3 setup.py install
elif [ "$1" = "install-req" ]; then
    python3 -m pip install -r requirements.txt --user
elif [ "$1" = "build-dist" ]; then
    python3 setup.py sdist bdist_wheel
elif [ "$1" = "clean" ]; then
    rm -rfv $(find . -name *.pyc) $(find . -name __pycache__) .coverage build/ dist/ dragonchain_sdk.egg-info/ docs/.build/
elif [ "$1" = "pr-test" ]; then
    set +e
    echo "\nChecking for linting errors\n"
    sh run.sh linter
    [ $? -ne 0 ] && echo "\nChecking for static security analysis issues\n" && exit 1
    sh run.sh bandit
    [ $? -ne 0 ] && echo "\n!!! Bandit (Security) Failure !!!" && exit 1
    echo "\nChecking that docs can build\n"
    sh run.sh docs
    [ $? -ne 0 ] && echo "\n!!! Docs Build Failure !!!" && exit 1
    echo "\nChecking that the entire project can build correctly\n"
    sh run.sh build
    [ $? -ne 0 ] && echo "\n!!! Build Failure !!!" && exit 1
    sh run.sh build-dist
    [ $? -ne 0 ] && echo "\n!!! Build Distribution Failure !!!" && exit 1
    echo "\nRunning all tests\n"
    sh run.sh tests
    [ $? -ne 0 ] && echo "\n!!! Tests Failure !!!" && exit 1
    echo "\nCleaning up\n"
    sh run.sh clean
    echo "\nSuccess!"
elif [ "$1" = "dist-release" ]; then
    python3 -m twine upload dist/*
else
    echo "$USAGE"
    exit 1
fi
