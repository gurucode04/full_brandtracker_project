#!/usr/bin/env bash
# Exit on error
set -o errexit

# Optimize pip for memory usage
export PIP_NO_CACHE_DIR=1
export PIP_DISABLE_PIP_VERSION_CHECK=1
export PIP_DEFAULT_TIMEOUT=60

# Install requirements based on lightweight mode
if [ "$USE_LIGHTWEIGHT_NLP" = "true" ]; then
    echo "Installing in ultra-lightweight mode (minimal dependencies)..."
    # Install core requirements with memory optimizations
    pip install --no-cache-dir -r requirements-lightweight.txt
else
    echo "Installing all dependencies including ML libraries..."
    # Try to install torch CPU-only first to save space
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu || pip install --no-cache-dir torch
    pip install --no-cache-dir -r requirements.txt
fi

# Make start script executable
chmod +x start.sh || true

# Convert static asset files (with memory optimization)
python manage.py collectstatic --no-input --clear || true

# Apply any outstanding database migrations
python manage.py migrate --noinput || true

