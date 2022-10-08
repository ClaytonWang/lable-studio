#!/usr/bin/env bash

export PYTHONPATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.."  && pwd)"
export ENV=DEV
python label_studio/manage.py runserver