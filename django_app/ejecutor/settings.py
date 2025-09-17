# ejecutor/settings.py (fragmento actualizado para producción en Azure)
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Detect Azure App Service environment and set a persistent data directory.
# On Azure App Service for Linux, the persistent writable path is /home.
AZURE_HOME = os.environ.get("HOME")  # Typically '/home' on Azure App Service Linux
PERSISTENT_DIR = Path(AZURE_HOME) if AZURE_HOME else None

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'clave-insegura')

DEBUG = False

ALLOWED_HOSTS = ['manufacturakos.azurewebsites.net']  # Puedes usar tuapp.azurewebsites.net

CSRF_TRUSTED_ORIGINS = ['https://manufacturakos.azurewebsites.net']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'scripts_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para servir archivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ejecutor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'scripts_app', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ejecutor.wsgi.application'

def _default_sqlite_name():
    """
    Choose SQLite location:
    - In Azure (HOME available), use /home/site/data/db.sqlite3 for persistence across deployments.
    - Locally, use the project BASE_DIR/db.sqlite3.
    """
    if PERSISTENT_DIR:
        data_dir = PERSISTENT_DIR / 'site' / 'data'
        os.makedirs(data_dir, exist_ok=True)
        return data_dir / 'db.sqlite3'
    return BASE_DIR / 'db.sqlite3'

# Allow switching DB engine via environment, default to SQLite for simplicity
DB_ENGINE = os.environ.get('DB_ENGINE', 'sqlite')  # 'sqlite' | 'mssql' | 'postgres'

if DB_ENGINE == 'mssql':
    # Example MSSQL configuration using django-mssql-backend and ODBC connection string
    # Provide env vars: MSSQL_NAME, MSSQL_USER, MSSQL_PASSWORD, MSSQL_HOST, MSSQL_PORT, MSSQL_OPTIONS (optional)
    DATABASES = {
        'default': {
            'ENGINE': 'django_mssql_backend',
            'NAME': os.environ.get('MSSQL_NAME', ''),
            'USER': os.environ.get('MSSQL_USER', ''),
            'PASSWORD': os.environ.get('MSSQL_PASSWORD', ''),
            'HOST': os.environ.get('MSSQL_HOST', ''),
            'PORT': os.environ.get('MSSQL_PORT', ''),
            'OPTIONS': {
                'driver': os.environ.get('MSSQL_DRIVER', 'ODBC Driver 18 for SQL Server'),
                # TrustServerCertificate is commonly needed on Azure SQL when not using full CA chain
                'extra_params': os.environ.get('MSSQL_EXTRA_PARAMS', 'TrustServerCertificate=yes;'),
            },
        }
    }
elif DB_ENGINE == 'postgres':
    # Optional: support Django DATABASE_URL if provided
    import urllib.parse as _urlparse
    DATABASE_URL = os.environ.get('DATABASE_URL', '')
    if DATABASE_URL:
        # Minimal parser for postgres://user:pass@host:port/dbname
        parsed = _urlparse.urlparse(DATABASE_URL)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': parsed.path.lstrip('/'),
                'USER': parsed.username,
                'PASSWORD': parsed.password,
                'HOST': parsed.hostname,
                'PORT': parsed.port or '',
            }
        }
    else:
        # Fallback to SQLite if DATABASE_URL missing
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': _default_sqlite_name(),
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': _default_sqlite_name(),
        }
    }

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'scripts_app/static')]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Login config
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'