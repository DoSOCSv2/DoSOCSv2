FROM ubuntu:latest

MAINTAINER Sai Uday Shankar Korlimarla "skorlimarla@unomaha.edu"

RUN apt-get update && \
    apt-get install -y git build-essential libpq-dev python python-pip python-dev lib2.0-dev &&\
    pip install psycopg2 && \
    git clone https://github.com/DoSOCSv2/DoSOCSv2.git DoSOCSv2 &&\
    cd DoSOCSv2 &&\
    pip install . &&\
    /bin/bash scripts/install-nomos.sh &&\
    cd ~ &&\
    dosocs2 dbinit --no-confirm
