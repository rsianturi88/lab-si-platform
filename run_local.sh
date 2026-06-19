#!/bin/bash
set -e
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if [ ! -f .env ]; then
cat > .env <<'ENV'
SECRET_KEY=dev-secret-key-change-before-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,.vercel.app
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,https://*.vercel.app
DATABASE_URL=sqlite:///db.sqlite3
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=ChangeMe123!
ENV
fi
python manage.py migrate
python manage.py bootstrap_labms
python manage.py bootstrap_enterprise
python manage.py runserver
