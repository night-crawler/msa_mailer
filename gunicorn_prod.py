import os

bind = ['0.0.0.0:8000']
workers = os.environ.get('GUNICORN_WORKERS', 4)
pid = '/application/run/gunicorn.pid'
reload = False
preload_app = True
chdir = '/application/msa_mailer/'
pythonpath = '/usr/local/bin/python'
raw_env = [
    'LANG=ru_RU.UTF-8',
    'LC_ALL=ru_RU.UTF-8',
    'LC_LANG=ru_RU.UTF-8'
]
user = 'msa_mailer'
group = 'msa_mailer'
accesslog = '/application/log/gunicorn.access.log'
errorlog = '/application/log/gunicorn.error.log'
timeout = os.environ.get('GUNICORN_TIMEOUT', 10)
