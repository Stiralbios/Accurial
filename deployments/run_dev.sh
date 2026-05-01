#!/bin/bash

shopt -s expand_aliases
. /root/.bashrc
poetry config virtualenvs.in-project false
poetry config virtualenvs.options.always-copy true
poetry install || rm -f poetry.lock && poetry install
VENV_PATH=$(poetry env info --path)
. "$VENV_PATH/bin/activate"
cd sources || exit
uvicorn backend.main:app --reload --host 0.0.0.0
