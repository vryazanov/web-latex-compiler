#!/bin/bash

flake8 web/

isort --check-only --quiet web/**/*.py
