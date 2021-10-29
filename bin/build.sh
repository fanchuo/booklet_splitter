#!/bin/bash

set -eu
cd $(dirname "$0")
cd ..
if [ ! -d venv ] ; then
  python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt
pip install -e .[tests]

while [ $# -gt 0 ] ; do
  case "$1" in
    test)
      python setup.py test
      ;;
    package)
      python setup.py bdist_wheel
      ;;
    cover)
      coverage run setup.py test
      coverage report
      coverage html
      ;;
    flake8)
      flake8 src/ tests/ scripts/booklets
      ;;
    black-check)
      black --check src/ tests/ scripts/booklets
      ;;
    black)
      black src/ tests/ scripts/booklets
      ;;
  esac
  shift
done
