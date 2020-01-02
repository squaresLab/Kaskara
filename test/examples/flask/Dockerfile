FROM ubuntu:18.04
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
RUN apt-get update \
 && apt-get install -y \
      git \
      python3 \
      python3-pip \
      sudo \
 && pip3 install \
      coverage \
      pytest \
      pytest-cov

WORKDIR /opt/flask
RUN git clone https://github.com/pallets/flask /opt/flask \
 && cd /opt/flask \
 && git checkout 1.1.1 \
 && pip3 install -e .
