FROM alpine:3.20.0
RUN apk add --no-cache git
WORKDIR /opt/flask
RUN git clone https://github.com/pallets/flask /opt/flask \
 && cd /opt/flask \
 && git checkout 1.1.1
