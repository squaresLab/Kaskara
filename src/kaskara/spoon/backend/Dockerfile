FROM ghcr.io/graalvm/native-image-community:17-muslib AS build
CMD ["/bin/bash"]
ENTRYPOINT ["/bin/bash", "-c"]
COPY . /tmp/kaskara-spoon
ENV KASKARA_SPOON_VERSION 0.1.0
RUN cd /tmp/kaskara-spoon \
 && mkdir -p /opt/kaskara-spoon/bin \
 && ./gradlew build \
 && cd ./build/libs \
 && java \
        -agentlib:native-image-agent=config-output-dir=META-INF/native-image \
        -jar ./kaskara-spoon-0.1.0-all.jar \
        /tmp/kaskara-spoon/src/main/java \
 && native-image \
        -classpath . \
        --verbose \
        --no-fallback \
        --static \
        --libc=musl \
        -jar ./kaskara-spoon-${KASKARA_SPOON_VERSION}-all.jar \
        -o /opt/kaskara-spoon/bin/kaskara-spoon \
 && /opt/kaskara-spoon/bin/kaskara-spoon --help \
 && /opt/kaskara-spoon/bin/kaskara-spoon /tmp/kaskara-spoon/src/main/java

FROM ghcr.io/graalvm/native-image-community:17-muslib AS run
COPY --from=build /opt/kaskara-spoon /opt/kaskara-spoon
RUN /opt/kaskara-spoon/bin/kaskara-spoon --help
