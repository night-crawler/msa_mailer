import logging
import os
import socket
import sys
import warnings

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

import structlog
from django_docker_helpers.config import (
    ConfigLoader, EnvironmentParser, YamlParser
)
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
MEDIA_ROOT = os.path.join(ROOT_PATH, 'media')

CKEDITOR_UPLOAD_PATH = os.path.join(MEDIA_ROOT, 'uploads')

LOCAL_SETTINGS_FILE = os.path.join(BASE_DIR, PROJECT_NAME, 'local_settings.py')

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
configure = ConfigLoader.from_env(
    extra={'endpoint': 'msa/mailer/config.yml'},
    suppress_logs=True,
    silent=True,
)
# -----------------------------------------------------------------------------
DEBUG = configure('debug', False, coerce_type=bool)

COMMON_BASE_HOST = configure('common.base.host', 'mailer.test')
COMMON_BASE_PORT = configure('common.base.port', 8000)  # 8282 etc
COMMON_BASE_SCHEME = configure('common.base.scheme', 'http')  # Either 'http' or 'https'

SECRET_KEY = configure('common.secret_key', 'secret')
SECRET_KEY == 'secret' and warnings.warn('SECRET_KEY is not assigned! Production unsafe!')

STATIC_URL = configure('static_url', '/static/')
MEDIA_URL = configure('media_url', '/media/')

SUPERUSER = {
    'username': configure('superuser.username'),
    'email': configure('superuser.email'),
    'password': configure('superuser.password'),
}

# --------------- HOSTS ---------------
HOSTNAME = socket.gethostname()

ALLOWED_HOSTS = [
    HOSTNAME,
    '127.0.0.1',
] + configure('hosts', [])

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
    'django_uwsgi',

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
        'ENGINE': configure('db.engine', 'django.db.backends.postgresql'),
        'HOST': configure('db.host', 'localhost'),
        'PORT': configure('db.port', ''),

        'NAME': configure('db.name', 'msa_mailer'),
        'USER': configure('db.user', 'msa_mailer'),
        'PASSWORD': configure('db.password', 'msa_mailer'),

        'CONN_MAX_AGE': configure('db.conn_max_age', 60, coerce_type=int),
    }
}

CACHES = {
    'default': {
        'KEY_PREFIX': 'msa_mailer',
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': configure('caches.locations', ['localhost:6379']),
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

TIME_ZONE = configure('time_zone', 'UTC')
USE_I18N = configure('use_i18n', True)
USE_L10N = configure('use_l10n', True)
USE_TZ = configure('use_tz', True)

SERVER_EMAIL = configure('mail.server_email')
EMAIL_USE_TLS = configure('mail.tls')
EMAIL_BACKEND = configure('mail.backend', 'django.core.mail.backends.smtp.EmailBackend')
DEFAULT_FROM_EMAIL = configure('mail.from', 'noreply@example.com')

EMAIL_HOST = configure('mail.host', 'example.com')
EMAIL_PORT = configure('mail.port', 587, coerce_type=int)
EMAIL_HOST_USER = configure('mail.user', 'example')
EMAIL_HOST_PASSWORD = configure('mail.password', '')

# --------------- BATTERIES ---------------
DB_MAILER_ENABLE_LOGGING = configure('dbmailer.enable_logging', True)
DB_MAILER_READ_ONLY_ENABLED = configure('dbmailer.read_only_enabled', False)
DB_MAILER_TRACK_ENABLE = configure('dbmailer.track_enable', True)
DB_MAILER_USE_CELERY_FOR_ADMIN_TEST = configure('dbmailer.use_celery_for_admin_test', False)
DB_MAILER_SHOW_CONTEXT = configure('dbmailer.show_context', False)

# django-db-mailer celery
BROKER_URL = configure('celery.broker', 'redis://127.0.0.1:6379/1')

# CELERY
CELERY_RESULT_BACKEND = configure('celery.result_backend', 'redis://127.0.0.1:6379/15')
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

CELERY_WORKERS = configure('celery.workers', 1)

# RAVEN
if configure('raven.dsn', None):
    import raven  # noqa

    INSTALLED_APPS += ['raven.contrib.django.raven_compat']
    RAVEN_CONFIG = {
        'dsn': configure('raven.dsn', None),
        'release': __version__,
    }

# ckeditor
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


# ======================================== LOGGING ========================================

timestamper = structlog.processors.TimeStamper(fmt='iso')
pre_chain = [
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    timestamper,
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'filters': {
        'static_fields': {
            '()': 'msa_mailer.logging.filters.StaticFieldFilter',
            'fields': {
                'project': 'MSA Mailer',
                'version': __version__,
                'environment': configure('environment', 'dev'),
            },
        },
    },

    'formatters': {
        'colored': {
            '()': structlog.stdlib.ProcessorFormatter,
            'processor': structlog.dev.ConsoleRenderer(colors=True),
            'foreign_pre_chain': pre_chain,
        },
    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
        },
        'gelf': {
            'class': 'graypy.GELFHandler',
            'host': configure('gelf.host', '127.0.0.1'),
            'port': configure('gelf.port', 12201, coerce_type=int),
            'filters': ['static_fields'],
        },
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['default', 'gelf'],
            'propagate': False,
        },
        'django': {
            'level': 'INFO',
            'handlers': ['default'],
            'propagate': False,
        },
    }
}


def graypy_structlog_processor(logger, method_name, event_dict):
    args = (event_dict.get('event', ''),)
    kwargs = {'extra': event_dict}
    return args, kwargs


structlog.configure_once(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        # structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        # structlog.processors.JSONRenderer(),
        graypy_structlog_processor
    ],
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# ====================================================================================

# REDEFINE
try:
    from .local_settings import *  # noqa
except ImportError:
    pass

configure.print_config_read_queue(use_color=True)
