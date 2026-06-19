from pathlib import Path
import os
import dj_database_url
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY', default='dev-only-change-me')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,.vercel.app', cast=Csv())
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='https://*.vercel.app,http://localhost:8000', cast=Csv())

INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
    'csp','accounts','memberships','activities','enterprise','audit',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware','django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware','audit.middleware.AuditMiddleware',
]
ROOT_URLCONF = 'labms.urls'
TEMPLATES = [{
    'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,
    'OPTIONS':{'context_processors':['django.template.context_processors.debug','django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}
}]
WSGI_APPLICATION='labms.wsgi.application'

DATABASE_URL=config('DATABASE_URL', default='sqlite:///'+str(BASE_DIR/'db.sqlite3'))
DATABASES={'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=('neon.tech' in DATABASE_URL or 'sslmode=require' in DATABASE_URL))}

AUTH_USER_MODEL='accounts.User'
AUTH_PASSWORD_VALIDATORS=[
 {'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
 {'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator','OPTIONS':{'min_length':10}},
 {'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},
 {'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LANGUAGE_CODE='id-id'
TIME_ZONE='Asia/Jakarta'
USE_I18N=True
USE_TZ=True
STATIC_URL='/static/'
STATIC_ROOT=BASE_DIR/'staticfiles'
STATICFILES_DIRS=[BASE_DIR/'static'] if (BASE_DIR/'static').exists() else []
STATICFILES_STORAGE='whitenoise.storage.CompressedManifestStaticFilesStorage'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
LOGIN_URL='login'
LOGIN_REDIRECT_URL='dashboard'
LOGOUT_REDIRECT_URL='login'

SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https')
SESSION_COOKIE_HTTPONLY=True
CSRF_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE='Lax'
CSRF_COOKIE_SAMESITE='Lax'
X_FRAME_OPTIONS='DENY'
SECURE_CONTENT_TYPE_NOSNIFF=True
REFERRER_POLICY='same-origin'
if not DEBUG:
    SECURE_SSL_REDIRECT=True
    SESSION_COOKIE_SECURE=True
    CSRF_COOKIE_SECURE=True

CSP_DEFAULT_SRC=("'self'",)
CSP_STYLE_SRC=("'self'", "'unsafe-inline'", 'cdn.jsdelivr.net')
CSP_SCRIPT_SRC=("'self'", "'unsafe-inline'", 'cdn.jsdelivr.net')
CSP_IMG_SRC=("'self'", 'data:')
CSP_FONT_SRC=("'self'", 'cdn.jsdelivr.net')

LOGGING={
 'version':1,'disable_existing_loggers':False,
 'handlers':{'console':{'class':'logging.StreamHandler'}},
 'root':{'handlers':['console'],'level':'INFO'},
 'loggers':{'django.security':{'handlers':['console'],'level':'WARNING','propagate':False}}
}
