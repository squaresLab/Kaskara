# TODO build JAR, run inside minimal JRE image
FROM openjdk:11-slim AS build
COPY . /opt/kaskara
WORKDIR /opt/kaskara
RUN ./gradlew build
CMD ["/bin/bash"]
ENTRYPOINT ["/bin/bash", "-c"]
