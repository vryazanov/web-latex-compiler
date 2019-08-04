#!/bin/bash

flake8 web/

isort --check-only --lines-after-imports 2 --quiet web/**/*.py
