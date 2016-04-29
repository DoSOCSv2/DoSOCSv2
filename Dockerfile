FROM ubuntu:latest

MAINTAINER Sai Uday Shankar Korlimarla "skorlimarla@unomaha.edu"

RUN apt-get update && \
    apt-get install -y git build-essential libpq-dev python python-pip python-dev lib2.0-dev &&\
    pip install psycopg2 && \
    git clone https://github.com/UShan89/DoSOCSv2.git DoSOCSv2 &&\
    cd DoSOCSv2 &&\
    pip install .

RUN rm /bin/sh && ln -s /bin/bash /bin/sh && "/DoSOCSv2/scripts/install-nomos-docker.sh"
