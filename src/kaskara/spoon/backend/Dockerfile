FROM ghcr.io/graalvm/native-image-community:17-muslib AS build
CMD ["/bin/bash"]
ENTRYPOINT ["/bin/bash", "-c"]
COPY . /tmp/kaskara-spoon
ENV KASKARA_SPOON_VERSION 0.1.0
RUN cd /tmp/kaskara-spoon \
 && mkdir -p /opt/kaskara-spoon/bin \
 && ./gradlew build \
 && native-image \
        --no-fallback \
        --static \
        --libc=musl \
        -jar ./build/libs/kaskara-spoon-${KASKARA_SPOON_VERSION}-all.jar \
        -o /opt/kaskara-spoon/bin/kaskara-spoon \
 && /opt/kaskara-spoon/bin/kaskara-spoon --help

FROM ghcr.io/graalvm/native-image-community:17-muslib AS run
COPY --from=build /opt/kaskara-spoon /opt/kaskara-spoon
RUN /opt/kaskara-spoon/bin/kaskara-spoon --help
