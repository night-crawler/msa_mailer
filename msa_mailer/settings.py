import os
import socket
import sys
import warnings

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django_docker_helpers.config import ConfigLoader, YamlParser, EnvironmentParser

from yaml import load

from . import __version__

SITE_ID = 1

# --------------- PATHS ---------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_PATH = BASE_DIR
PROJECT_PATH = ROOT_PATH
PROJECT_NAME = os.path.basename(ROOT_PATH)
PROJECT_DATA_DIR = os.path.join(BASE_DIR, PROJECT_NAME, 'data')
__TEMPLATE_DIR = os.path.join(BASE_DIR, PROJECT_NAME, 'templates')
__LOCALE_PATH = os.path.abspath(os.path.join(ROOT_PATH, 'locale'))

VIRTUAL_ENV_DIR = os.path.abspath(os.path.join(BASE_DIR, os.path.pardir))

STATIC_ROOT = os.path.join(ROOT_PATH, 'static')
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(ROOT_PATH, 'media')
MEDIA_URL = '/media/'

CKEDITOR_UPLOAD_PATH = os.path.join(MEDIA_ROOT, 'uploads')

LOCAL_SETTINGS_FILE = os.path.join(BASE_DIR, PROJECT_NAME, 'local_settings.py')
SECRET_SETTINGS_FILE = os.path.join(BASE_DIR, PROJECT_NAME, 'secret_settings.py')

# --------------- GENERATORS ---------------
for path in [
    STATIC_ROOT, MEDIA_ROOT, PROJECT_DATA_DIR, __TEMPLATE_DIR, __LOCALE_PATH, CKEDITOR_UPLOAD_PATH
]:
    if not os.path.exists(path):
        os.makedirs(path, mode=0o755, exist_ok=True)

# ------------------------------ LOAD YAML CONFIG -----------------------------
_config_name = os.environ.get('DJANGO_CONFIG_FILE_NAME', 'without-docker.yml')
config_path = os.path.join(BASE_DIR, 'msa_mailer', 'config', _config_name)

os.environ.setdefault('YAMLPARSER__CONFIG', config_path)
config = ConfigLoader.from_env(
    extra={'endpoint': 'msa/mailer/config.yml'},
    suppress_logs=True,
    silent=True,
)
# -----------------------------------------------------------------------------

COMMON_BASE_HOST = config.get('common.base.host', 'mailer.test')
COMMON_BASE_PORT = config.get('common.base.port', 8000)  # 8282 etc
COMMON_BASE_SCHEME = config.get('common.base.scheme', 'http')  # Either 'http' or 'https'

SUPERUSER = {
    'username': config.get('superuser.username'),
    'email': config.get('superuser.email'),
    'password': config.get('superuser.password'),
}

DEBUG = config.get('debug', False)

# --------------- SECRET SETTINGS ---------------
SECRET_KEY = config.get('common.secret_key', 'secret')

if SECRET_KEY == 'secret':
    warnings.warn('SECRET_KEY is not assigned! Production unsafe!')

# --------------- HOSTS ---------------
HOSTNAME = socket.gethostname()

ALLOWED_HOSTS = [
    HOSTNAME,
    '127.0.0.1',
] + config.get('hosts', [])

# --------------- DJANGO STANDARD ---------------
INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'dbtemplates',
    'dbmail',
    'ckeditor',
    'ckeditor_uploader',
    'reversion',
    # 'reversion_compare',

    'common',
    'frontend',
]

ROOT_URLCONF = 'msa_mailer.urls'

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',

    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [__TEMPLATE_DIR],
        # 'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.csrf',
                'django.template.context_processors.tz',
                'django.template.context_processors.static',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'django.template.loaders.eggs.Loader',
                'dbtemplates.loader.Loader',
            ],
        },
    },
]

WSGI_APPLICATION = 'msa_mailer.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': config.get('db.name', 'django.db.backends.postgresql'),
        'HOST': config.get('db.host', 'localhost'),
        'PORT': config.get('db.port', ''),

        'NAME': config.get('db.database', 'msa_mailer'),
        'USER': config.get('db.user', 'msa_mailer'),
        'PASSWORD': config.get('db.password', 'msa_mailer'),

        'CONN_MAX_AGE': config.get('db.conn_max_age', 60, coerce_type=int),
    }
}

CACHES = {
    'default': {
        'KEY_PREFIX': 'msa_mailer',
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': config.get('cache.locations', ['localhost:6379']),
        'OPTIONS': {
            'DB': 8,
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 20,
            },
            'MAX_CONNECTIONS': 1000,
            'PICKLE_VERSION': 2,
        },
    },
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOCALE_PATHS = (__LOCALE_PATH,)
LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('en', _('English')),
    ('ru', _('Russian')),
)

MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'
MODELTRANSLATION_LANGUAGES = ('ru', 'en')
MODELTRANSLATION_TRANSLATION_FILES = (
    'dbmail.translation',
)

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

SERVER_EMAIL = config.get('mail.server_email')
EMAIL_USE_TLS = config.get('mail.tls')
EMAIL_BACKEND = config.get('mail.backend', 'django.core.mail.backends.smtp.EmailBackend')
DEFAULT_FROM_EMAIL = config.get('mail.from', 'noreply@example.com')

EMAIL_HOST = config.get('mail.host', 'example.com')
EMAIL_PORT = config.get('mail.port', 587)
EMAIL_HOST_USER = config.get('mail.user', 'example')
EMAIL_HOST_PASSWORD = config.get('mail.password', '')

# --------------- BATTERIES ---------------
DB_MAILER_ENABLE_LOGGING = config.get('dbmailer.enable_logging', False)
DB_MAILER_READ_ONLY_ENABLED = config.get('dbmailer.read_only_enabled', False)
DB_MAILER_TRACK_ENABLE = config.get('dbmailer.track_enable', True)
DB_MAILER_USE_CELERY_FOR_ADMIN_TEST = config.get('dbmailer.use_celery_for_admin_test', False)
DB_MAILER_SHOW_CONTEXT = config.get('dbmailer.show_context', False)

# django-db-mailer celery
BROKER_URL = config.get('celery.broker', 'redis://127.0.0.1:6379/1')

# CELERY
CELERY_RESULT_BACKEND = config.get('celery.result_backend', 'redis://127.0.0.1:6379/15')
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_ACKS_LATE = True
CELERYD_PREFETCH_MULTIPLIER = 1
# use priority steps only for mail queue
if 'mail_messages' in sys.argv:
    BROKER_TRANSPORT_OPTIONS = {
        'priority_steps': list(range(10)),
    }
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_DEFAULT_QUEUE = 'default'

CELERY_WORKERS = config.get('celery.workers', 1)

# RAVEN
if config.get('raven', False) and config.get('raven.dsn', None):
    import raven  # noqa

    INSTALLED_APPS += ['raven.contrib.django.raven_compat']
    RAVEN_CONFIG = {
        'dsn': config.get('raven.dsn', None),
        'release': __version__,
    }


CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 500,
        'width': '100%',
        'allowedContent': True,
        'removePlugins': 'stylesheetparser',
        'extraAllowedContent': '*(*){*}[*]',
        'fullPage': True
    },
}

# REDEFINE
try:
    from .local_settings import *  # noqa
except ImportError:
    pass

config.print_config_read_queue(use_color=True)
