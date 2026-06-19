#!/usr/bin/env bash
set -o errexit

echo "=== Python version ==="
python --version

echo "=== Installing dependencies ==="
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "=== Django check ==="
python manage.py check

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput --clear

echo "=== Build completed successfully ==="