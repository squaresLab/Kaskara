FROM ubuntu:24.04 AS test-donor
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /tests

ENV JENKINS_REVISION jenkins-2.464
RUN git clone https://github.com/jenkinsci/jenkins \
 && git -C jenkins checkout ${JENKINS_REVISION}

ENV SPRING_BOOT_REVISION v3.3.1
RUN git clone https://github.com/spring-projects/spring-boot \
 && git -C spring-boot checkout ${SPRING_BOOT_REVISION}

ENV ELASTIC_SEARCH_REVISION v8.14.1
RUN git clone https://github.com/elastic/elasticsearch \
 && git -C elasticsearch checkout ${ELASTIC_SEARCH_REVISION}

ENV GUAVA_REVISION v33.2.1
RUN git clone https://github.com/google/guava \
 && git -C guava checkout ${GUAVA_REVISION}

ENV DUBBO_REVISION dubbo-3.2.14
RUN git clone https://github.com/apache/dubbo \
 && git -C dubbo checkout ${DUBBO_REVISION}


# FROM ghcr.io/graalvm/native-image-community:21-muslib AS jar-builder
FROM openjdk:21-slim AS jar-builder
COPY . /tmp/kaskara-spoon
ENV KASKARA_SPOON_VERSION 0.1.0
RUN cd /tmp/kaskara-spoon \
 && ./gradlew build \
 && mv /tmp/kaskara-spoon/build/libs/kaskara-spoon-${KASKARA_SPOON_VERSION}-all.jar /tmp/kaskara-spoon/build/libs/kaskara-spoon.jar


FROM ghcr.io/graalvm/native-image-community:21-muslib AS native-image-builder
CMD ["/bin/bash"]
ENTRYPOINT ["/bin/bash", "-c"]
COPY --from=test-donor /tests /tests
COPY --from=jar-builder /tmp/kaskara-spoon/build/libs /tmp/kaskara-spoon/build/libs

RUN cd /tmp/kaskara-spoon/build/libs \
 && mkdir -p META-INF/native-image \
 && echo "test: kaskara-spoon (src/main/java)" \
 && java \
        -agentlib:native-image-agent=config-output-dir=META-INF/native-image \
        -jar ./kaskara-spoon.jar \
        /tmp/kaskara-spoon/src/main/java \
 && echo "test: jenkins (core/src/main/java)" \
 && java \
        -agentlib:native-image-agent=config-merge-dir=META-INF/native-image \
        -jar ./kaskara-spoon.jar \
        /tests/jenkins/core/src/main/java \
 && echo "skipping test: guava (guava)" \
 && echo "skipping test: spring-boot (spring-boot-project/spring-boot/src/main/java)" \
 && echo "skipping test: elasticsearch"

# && echo "test: guava (guava)" \
# && java \
#        -agentlib:native-image-agent=config-merge-dir=META-INF/native-image \
#        -jar ./kaskara-spoon.jar \
#        /tests/guava/guava \

# --no-fallback
RUN cd /tmp/kaskara-spoon/build/libs \
 && mkdir -p /opt/kaskara-spoon/bin \
 && native-image \
        -classpath . \
        --no-fallback \
        --verbose \
        --static \
        --libc=musl \
        -H:+ReportExceptionStackTraces \
        -jar ./kaskara-spoon.jar \
        -o /opt/kaskara-spoon/bin/kaskara-spoon \
 && /opt/kaskara-spoon/bin/kaskara-spoon --help \
 && /opt/kaskara-spoon/bin/kaskara-spoon /tmp/kaskara-spoon/src/main/java


FROM ubuntu:24.04 AS package
COPY --from=native-image-builder /opt/kaskara-spoon /opt/kaskara-spoon
RUN /opt/kaskara-spoon/bin/kaskara-spoon --help
