#!/usr/bin/env python
import os
import sys

from django.conf import settings
from django_docker_helpers.db import ensure_databases_alive, ensure_caches_alive, migrate, \
    modeltranslation_sync_translation_fields
from django_docker_helpers.files import collect_static
from django_docker_helpers.management import create_admin, run_gunicorn
from django_docker_helpers.utils import env_bool_flag

from msa_mailer.wsgi import application

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'msa_mailer.settings')

    if env_bool_flag('CHECK_CONNECTIONS'):
        ensure_databases_alive(100)
        ensure_caches_alive(100)

    if env_bool_flag('RUN_PREPARE'):
        collect_static()
        migrate()
        modeltranslation_sync_translation_fields()
        create_admin('SUPERUSER')

    if len(sys.argv) == 2:
        if sys.argv[1] == 'gunicorn':
            gunicorn_module_name = os.getenv('GUNICORN_MODULE_NAME', 'gunicorn_dev')
            run_gunicorn(application, gunicorn_module_name=gunicorn_module_name)
            exit(0)

        if sys.argv[1] == 'celery':
            from msa_mailer.celery import app as celery_app

            celery_app.start(argv=['celery', 'worker', '-B', '-c', str(settings.CELERY_WORKERS), '-l', 'info'])
            exit(0)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
