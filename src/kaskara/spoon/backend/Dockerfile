FROM openjdk:17-slim AS jar-builder
COPY . /tmp/kaskara-spoon
ENV KASKARA_SPOON_VERSION 0.1.0
RUN mkdir -p /opt/kaskara-spoon \
 && cd /tmp/kaskara-spoon \
 && ./gradlew build \
 && mv /tmp/kaskara-spoon/build/libs/kaskara-spoon-${KASKARA_SPOON_VERSION}-all.jar /opt/kaskara-spoon/kaskara-spoon.jar \
 && cd /opt/kaskara-spoon \
 && rm -rf /tmp/* \
 && java -jar /opt/kaskara-spoon/kaskara-spoon.jar --help
