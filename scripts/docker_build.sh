#!/usr/bin/env bash

docker build -t ncrawler/msa_mailer:latest \
             -t ncrawler/msa_mailer:0.1.3 \
             .

#docker-squash -t ncrawler/msa_mailer:latest-squashed ncrawler/msa_mailer:latest
#docker tag ncrawler/msa_mailer:latest-squashed ncrawler/msa_mailer:0.1.3-squashed
