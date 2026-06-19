#!/usr/bin/env bash
set -o errexit

echo "=== Build Lab SI Platform for Vercel ==="

echo "=== Python version ==="
python --version

echo "=== Install dependencies with uv-managed Python compatibility ==="
python -m pip install --break-system-packages -r requirements.txt

echo "=== Django system check ==="
python manage.py check

echo "=== Collect static files ==="
python manage.py collectstatic --noinput --clear

echo "=== Build completed successfully ==="