# https://stackoverflow.com/questions/40431161/clang-tool-cannot-find-required-libraries-on-ubuntu-16-10
FROM christimperley/llvm18 as cpp

# install compile-time dependencies
RUN apt-get update \
 && apt-get install -y \
        gdb \
        less \
        libssl-dev \
        vim \
        wget \
        zip

# install fmt
ARG FMT_VERSION=10.2.1
RUN cd /tmp \
 && wget -nv "https://github.com/fmtlib/fmt/archive/${FMT_VERSION}.tar.gz" \
 && tar -xf "${FMT_VERSION}.tar.gz" \
 && cd "fmt-${FMT_VERSION}" \
 && mkdir build \
 && cd build \
 && cmake .. \
 && make -j4 \
 && make install \
 && rm -rf /tmp/*

# install nlohmann/json
ARG NLOHMANN_JSON_VERSION=3.11.3
RUN cd /tmp \
 && wget -nv "https://github.com/nlohmann/json/archive/v${NLOHMANN_JSON_VERSION}.tar.gz" \
 && tar -xf "v${NLOHMANN_JSON_VERSION}.tar.gz" \
 && cd json* \
 && mkdir build \
 && cd build \
 && cmake .. \
 && make -j4 \
 && make install \
 && rm -rf /tmp/*

# build and install
ADD . /tmp/kaskara
RUN mkdir /tmp/kaskara/build && \
    cd /tmp/kaskara/build && \
    cmake .. && \
    make -j4
RUN mkdir -p /opt/kaskara/bin \
 && cp /tmp/kaskara/build/src/kaskara-loop-finder /opt/kaskara/bin \
 && cp /tmp/kaskara/build/src/kaskara-statement-finder /opt/kaskara/bin \
 && cp /tmp/kaskara/build/src/kaskara-function-scanner /opt/kaskara/bin \
 && cp /tmp/kaskara/build/src/kaskara-insertion-point-finder /opt/kaskara/bin \
 && cp /tmp/kaskara/build/src/kaskara-snippet-extractor /opt/kaskara/bin

RUN mkdir -p /opt/kaskara/clang \
 && cp -r /opt/llvm/lib/clang/18/include/* /opt/kaskara/clang

# install scripts
FROM alpine:3.7 as minimal
COPY --from=cpp /opt/kaskara /opt/kaskara
COPY scripts /opt/kaskara/scripts
WORKDIR /opt/kaskara
ENV PATH "/opt/kaskara/scripts:${PATH}"
VOLUME /opt/kaskara