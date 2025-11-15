#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install requirements based on lightweight mode
if [ "$USE_LIGHTWEIGHT_NLP" = "true" ]; then
    echo "Installing in lightweight mode (skipping heavy ML libraries)..."
    pip install -r requirements-lightweight.txt
else
    echo "Installing all dependencies including ML libraries..."
    # Try to install torch CPU-only first to save space
    pip install torch --index-url https://download.pytorch.org/whl/cpu || pip install torch
    pip install -r requirements.txt
fi

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

