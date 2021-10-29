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
    pip install -e .[tests]
  fi
}

while [ $# -gt 0 ] ; do
  case "$1" in
    test)
      ensure_installed
      python setup.py test
      ;;
    package)
      python setup.py bdist_wheel
      ;;
    cover)
      ensure_installed
      coverage run setup.py test
      coverage report
      coverage html
      ;;
    flake8)
      ensure_installed
      flake8 src/ tests/ scripts/booklets
      ;;
    black-check)
      ensure_installed
      black --check src/ tests/ scripts/booklets
      ;;
    black)
      ensure_installed
      black src/ tests/ scripts/booklets
      ;;
  esac
  shift
done
