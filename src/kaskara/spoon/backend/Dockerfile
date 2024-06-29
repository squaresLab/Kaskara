FROM openjdk:17-slim AS build
COPY . /opt/kaskara-spoon
WORKDIR /opt/kaskara-spoon
RUN ./gradlew build \
 && ./gradlew installDist

FROM openjdk:17-slim AS run
WORKDIR /opt/kaskara-spoon
ENV PATH "/opt/kaskara-spoon/bin:${PATH}"
CMD ["/bin/bash"]
ENTRYPOINT ["/bin/bash", "-c"]
COPY --from=build /opt/kaskara-spoon/build/install/kaskara-spoon /opt/kaskara-spoon
