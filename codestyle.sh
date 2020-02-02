#!/bin/bash

flake8 web/

isort --lines-after-imports 2 --apply -y --quiet **/*.py
