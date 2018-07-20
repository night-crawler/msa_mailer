import os

from django.core.wsgi import get_wsgi_application

from raven.contrib.django.middleware.wsgi import Sentry

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'msa_mailer.settings')

application = Sentry(get_wsgi_application())
