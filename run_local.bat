@echo off
setlocal
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo Python tidak ditemukan. Install Python 3.12/3.13 dan centang Add Python to PATH.
  pause
  exit /b 1
)
if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist .env (
  > .env echo SECRET_KEY=dev-secret-key-change-before-production
  >> .env echo DEBUG=True
  >> .env echo ALLOWED_HOSTS=localhost,127.0.0.1,.vercel.app
  >> .env echo CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,https://*.vercel.app
  >> .env echo DATABASE_URL=sqlite:///db.sqlite3
  >> .env echo DJANGO_SUPERUSER_USERNAME=admin
  >> .env echo DJANGO_SUPERUSER_EMAIL=admin@example.com
  >> .env echo DJANGO_SUPERUSER_PASSWORD=ChangeMe123!
)
python manage.py migrate
python manage.py bootstrap_labms
python manage.py bootstrap_enterprise
python manage.py runserver
pause
