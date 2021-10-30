#!/bin/bash

set -eu
cd $(dirname "$0")
cd ..
if [ ! -d venv ] ; then
  python3 -m venv venv
fi

source venv/bin/activate
if ! pip show --quiet wheel ; then
  pip install -r requirements.txt
fi
ensure_installed() {
  if ! pip show --quiet booklet_splitter ; then
    pip install -e .
  fi
}

ensure_installed_tests() {
  if ! pip show --quiet flake8 ; then
    pip install -e .[tests]
  fi
}

export VERSION=""
if [ ! -z "${GITHUB_REF+x}" ] ; then
  VERSION=$(echo "$GITHUB_REF" | sed -n -e 's/^refs\/tags\/v\([0-9]\+[.0-9]*\)$/\1/ p')
fi
if [ -z "$VERSION" ] ; then
  VERSION=dev
fi

while [ $# -gt 0 ] ; do
  case "$1" in
    test)
      ensure_installed
      python setup.py test
      ;;
    package)
      python setup.py bdist_wheel
      ;;
    publish)
      ensure_installed_tests
      export TWINE_USERNAME="__token__"
      export TWINE_PASSWORD="$PYPI_API_TOKEN"
      export TWINE_NON_INTERACTIVE=1
      twine upload dist/*
      ;;
    cover)
      ensure_installed_tests
      coverage run setup.py test
      coverage report
      coverage html
      coverage xml
      ;;
    flake8)
      ensure_installed_tests
      flake8 src/ tests/ scripts/booklets
      ;;
    black-check)
      ensure_installed_tests
      black --check src/ tests/ scripts/booklets
      ;;
    black)
      ensure_installed_tests
      black src/ tests/ scripts/booklets
      ;;
  esac
  shift
done
