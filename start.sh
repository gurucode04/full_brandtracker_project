#!/usr/bin/env bash
# Startup script that uses PORT environment variable
# Defaults to 8000 if PORT is not set

PORT=${PORT:-8000}

echo "Starting application on port $PORT"

exec python -m gunicorn brandtracker.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --workers ${WEB_CONCURRENCY:-2}

