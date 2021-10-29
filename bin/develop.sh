#!/bin/bash

if [ -z ${BIN_DIR+x} ] ; then
  BIN_DIR=$(dirname "$0")
  export BIN_DIR
  exec /bin/bash --init-file "$0"
fi

if [ -f /etc/bash.bashrc ] ; then
  source /etc/bash.bashrc
fi
if [ -f ~/.bashrc ] ; then
  source ~/.bashrc
fi
ROOT_DIR=$(cd "$BIN_DIR" ; cd .. ; pwd)
VENV_DIR="$ROOT_DIR"/venv
if [ ! -d "$ROOT_DIR"/venv ] ; then
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR"/bin/activate
pip install -r "$ROOT_DIR"/requirements.txt
pip install -e "$ROOT_DIR"[tests]
