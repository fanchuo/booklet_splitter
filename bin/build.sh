#!/bin/bash

set -eu
cd $(dirname "$0")
cd ..
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
  unset VERSION
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
      pytest --cov=src/ --cov-report=html --cov-report=xml
      ;;
    flake8)
      ensure_installed_tests
      flake8 src/ tests/ scripts/pdf_splitter setup.py
      ;;
    black-check)
      ensure_installed_tests
      black --check . scripts/pdf_splitter
      ;;
    black)
      ensure_installed_tests
      black . scripts/pdf_splitter
      ;;
    mypy)
      ensure_installed_tests
      mypy src/ scripts/pdf_splitter
      ;;
    pre-commit)
      ensure_installed_tests
      pre-commit run -a
      ;;
  esac
  shift
done
