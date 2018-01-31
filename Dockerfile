FROM python:3.6.4-slim-stretch

ENV BUILD_DEPS \
    build-essential \
    git-core \
    libgeoip-dev

ENV RUN_DEPS \
    libgeoip1 \
    gettext \
    libhiredis0.13 \
    geoip-bin \
    geoip-database

RUN apt-get update \
 && apt-get --assume-yes upgrade \
 && pip3 install wheel \
 && apt-get install --no-install-recommends --assume-yes ${BUILD_DEPS} ${RUN_DEPS} \
 && apt-get autoremove --assume-yes \
 && apt-get autoclean \
 && apt-get clean

WORKDIR /application/msa_mailer
ADD requirements.txt /application/msa_mailer
ADD requirements /application/msa_mailer/requirements
RUN pip install --src /usr/local/src --no-cache-dir -r requirements/prod.txt

RUN apt-get remove --purge --assume-yes $BUILD_DEPS && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get autoremove --assume-yes

ADD . /application/msa_mailer

# create static to prevent root owning of the static volume
# https://github.com/docker/compose/issues/3270#issuecomment-206214034
RUN mkdir /application/log && \
    mkdir /application/run && \
    mkdir /application/msa_mailer/static

RUN adduser --uid 1000 --home /application --disabled-password --gecos "" msa_mailer && \
    chown -hR msa_mailer: /application

# FIX [Errno 0] Bad magic number: '/usr/local/lib/python3.6/site-packages/dbtemplates/locale/ru/LC_MESSAGES/django.mo'
RUN rm -rf /usr/local/lib/python3.6/site-packages/dbtemplates/locale/

USER msa_mailer
ENV PYTHONUNBUFFERED=1
ENV DOCKERIZED=1

EXPOSE 8000
ENTRYPOINT ["python", "manage.py"]
CMD ["gunicorn"]
