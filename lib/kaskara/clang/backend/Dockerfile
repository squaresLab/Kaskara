# https://stackoverflow.com/questions/40431161/clang-tool-cannot-find-required-libraries-on-ubuntu-16-10
# FROM christimperley/clang as cpp
FROM christimperley/llvm11 as cpp

# install compile-time dependencies
RUN apt-get update && \
    apt-get install -y vim gdb wget zip less

# install fmt
RUN cd /tmp \
 && wget https://github.com/fmtlib/fmt/archive/5.0.0.tar.gz \
 && tar -xf 5.0.0.tar.gz \
 && cd fmt-5.0.0 \
 && mkdir build \
 && cd build \
 && cmake .. \
 && make -j4 \
 && make install \
 && rm -rf /tmp/*

# install nlohmann/json
RUN cd /tmp \
 && wget -nv https://github.com/nlohmann/json/archive/v3.1.2.tar.gz \
 && tar -xf v3.1.2.tar.gz \
 && cd json* \
 && mkdir build \
 && cd build \
 && cmake -DCMAKE_BUILD_TYPE=Debug .. \
 && make -j4 \
 && make install \
 && rm -rf /tmp/*

# build and install
ADD . /tmp/kaskara
RUN mkdir /tmp/kaskara/build \
 && cd /tmp/kaskara/build \
 && cmake \
      -DCMAKE_BUILD_TYPE=Debug \
      -DCMAKE_PREFIX_PATH=/opt/llvm11 \
      -DCMAKE_CXX_COMPILER=/opt/llvm11/bin/clang++ \
      -DCMAKE_LINKER=/opt/llvm11/bin/lld \
      -DCMAKE_CXX_FLAGS="-I/opt/llvm11/include -g -std=c++14 -D_GNU_SOURCE -D__STDC_CONSTANT_MACROS -D__STDC_FORMAT_MACROS -D__STDC_LIMIT_MACROS" \
      .. \
 && make -j4
RUN mkdir -p /opt/kaskara/bin \
 && cp /tmp/kaskara/build/src/kaskara-loop-finder /opt/kaskara/bin \
 && cp /tmp/kaskara/build/src/kaskara-statement-finder /opt/kaskara/bin \
 && cp /tmp/kaskara/build/src/kaskara-function-scanner /opt/kaskara/bin \
 && cp /tmp/kaskara/build/src/kaskara-insertion-point-finder /opt/kaskara/bin \
 && cp /tmp/kaskara/build/src/kaskara-snippet-extractor /opt/kaskara/bin
RUN mkdir -p /opt/kaskara/clang \
 && cp -r /opt/llvm11/include/* /opt/kaskara/clang

# install scripts
FROM alpine:3.7 as minimal
COPY --from=cpp /opt/kaskara /opt/kaskara
COPY scripts /opt/kaskara/scripts
WORKDIR /opt/kaskara
ENV PATH "/opt/kaskara/scripts:${PATH}"
VOLUME /opt/kaskara
