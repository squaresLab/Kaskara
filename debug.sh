#!/bin/bash
   docker build -t squareslab/kaskara . \
&& docker create --name kaskara squareslab/kaskara \
&& docker run --volumes-from kaskara --rm -it squareslab/manybugs:python-69223-69224 \
  /opt/kaskara/scripts/kaskara-loop-finder /experiment/src/Modules/binascii.c
docker rm -f kaskara
