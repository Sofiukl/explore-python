#!/bin/sh
export FLASK_APP=./cashman/index.py
export FLASK_ENV=development
source $(pipenv --venv)/bin/activate
flask run --debugger -h 0.0.0.0 --port 5000