#!/usr/bin/env bash
# Startup script that uses PORT environment variable
# Defaults to 8000 if PORT is not set

PORT=${PORT:-8000}

echo "Starting application on port $PORT"

# Optimize Python for memory usage
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export PYTHONHASHSEED=0

# Use single worker with memory optimizations
exec python -m gunicorn brandtracker.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 2 \
    --timeout 120 \
    --max-requests 500 \
    --max-requests-jitter 50 \
    --preload

