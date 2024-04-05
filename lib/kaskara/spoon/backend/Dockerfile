FROM eclipse-temurin:21 AS build
COPY . /opt/kaskara
WORKDIR /opt/kaskara
RUN pwd
RUN ls
RUN ./gradlew build \
 && ./gradlew installDist

FROM eclipse-temurin:21 AS run
WORKDIR /opt/kaskara
ENV PATH "/opt/kaskara/bin:${PATH}"
CMD ["/bin/bash"]
ENTRYPOINT ["/bin/bash", "-c"]
COPY --from=build /opt/kaskara/build/install/kaskara /opt/kaskara
