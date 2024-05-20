FROM openjdk:11-slim AS build
COPY . /opt/kaskara
WORKDIR /opt/kaskara
RUN ./gradlew build \
 && ./gradlew installDist

FROM openjdk:11-slim AS run
WORKDIR /opt/kaskara
ENV PATH "/opt/kaskara/bin:${PATH}"
CMD ["/bin/bash"]
ENTRYPOINT ["/bin/bash", "-c"]
COPY --from=build /opt/kaskara/build/install/kaskara /opt/kaskara
