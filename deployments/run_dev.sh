#!/bin/bash

shopt -s expand_aliases
. /root/.bashrc
poetry config virtualenvs.in-project true
poetry config virtualenvs.options.always-copy true
poetry install || rm -f poetry.lock && poetry install
. .venv/bin/activate
cd sources || exit
uvicorn backend.main:app --reload --host 0.0.0.0
