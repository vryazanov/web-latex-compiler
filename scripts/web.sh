#!/bin/sh
gunicorn --bind 0.0.0.0:$PORT --access-logfile - --error-logfile - "web:create_app()"
