#!/bin/sh
set -e
# Makes sure we're in this script's directory (avoid symlinks and escape special chars)
cd "$(cd "$(dirname "$0")"; pwd -P)"

USAGE="usage: run.sh [command]

command
unit         : run unit tests on the project
integration  : run integration tests on the project
coverage     : run the coverage report (only works after tests have been run)
tests        : run all tests on the project, including a unittest coverage report
lint         : run the linting and formatting checks against the project
format       : run black to auto-format the project
bandit       : run security linting with bandit against the project
build        : build the project from source
docs         : generate the docs and place them into docs/.build
install      : install the project from source (depends on running build first)
install-req  : install the python dependencies to dev on the project
build-dist   : build the distribution artifcats for the project from source
clean        : remove compiled python/docs/other build or distrubition artifacts from the local project
full-build   : run all of the tests that the pull request/build would check, locally
dist-release : upload and distribute the artifacts from build-dist to pypi"

if [ $# -lt 1 ]; then
    printf "%s\\n" "$USAGE"
    exit 1
elif [ "$1" = "unit" ]; then
    python3 -m coverage run --branch -m unittest discover -s tests/unit -p "test_*.py"
elif [ "$1" = "integration" ]; then
    python3 -m unittest discover -s tests/integration -p "test_*.py"
elif [ "$1" = "coverage" ]; then
    include=$(find ./dragonchain_sdk/ -path "*.py" | tr '\n' ',' | rev | cut -c 2- | rev)
    python3 -m coverage report -m --include="$include"
    python3 -m coverage xml --include="$include"
elif [ "$1" = "tests" ]; then
    printf "Running unit tests\\n"
    sh run.sh unit
    sh run.sh coverage
    printf "\\nRunning integration tests\\n"
    sh run.sh integration
elif [ "$1" = "lint" ]; then
    find . -name "*.py" -exec python3 -m flake8 {} +
    if [ "$2" != "no-format" ]; then python3 -m black --check -l 150 -t py34 .; fi
elif [ "$1" = "format" ]; then
    python3 -m black -l 150 -t py34 .
elif [ "$1" = "bandit" ]; then
    python3 -m bandit -r .
elif [ "$1" = "build" ]; then
    python3 setup.py build
elif [ "$1" = "docs" ]; then
    (
    cd docs || exit 1
    make html
    )
elif [ "$1" = "install" ]; then
    python3 setup.py install
elif [ "$1" = "install-req" ]; then
    python3 -m pip install -r requirements.txt
    if [ "$2" != "skip-extras" ]; then python3 -m pip install -r dev_requirements.txt; fi
elif [ "$1" = "build-dist" ]; then
    python3 setup.py sdist bdist_wheel
elif [ "$1" = "clean" ]; then
    find . -name __pycache__ -exec rm -rfv {} +
    rm -rfv .coverage coverage.xml build/ dist/ dragonchain_sdk.egg-info/ docs/.build/
elif [ "$1" = "full-build" ]; then
    set +e
    printf "\\nChecking for linting errors\\n\\n"
    if ! sh run.sh lint "$2"; then printf "\\n!!! Linting Failure. You may need to run 'run.sh format' !!!\\n" && exit 1; fi
    printf "\\nChecking for static security analysis issues\\n\\n"
    if ! sh run.sh bandit; then printf "\\n!!! Bandit (Security) Failure !!!\\n" && exit 1; fi
    printf "\\nChecking that docs can build\\n\\n"
    if ! sh run.sh docs; then printf "\\n!!! Docs Build Failure !!!\\n" && exit 1; fi
    printf "\\nChecking that the entire project can build correctly\\n\\n"
    if ! sh run.sh build; then printf "\\n!!! Build Failure !!!\\n" && exit 1; fi
    if ! sh run.sh build-dist; then printf "\\n!!! Build Distribution Failure !!!\\n" && exit 1; fi
    printf "\\nRunning all tests\\n\\n"
    if ! sh run.sh tests; then printf "\\n!!! Tests Failure !!!\\n" && exit 1; fi
    printf "\\nSuccess!\\nUse 'run.sh clean' to cleanup if desired\\n"
elif [ "$1" = "dist-release" ]; then
    python3 -m twine upload dist/*
else
    printf "%s\\n" "$USAGE"
    exit 1
fi
