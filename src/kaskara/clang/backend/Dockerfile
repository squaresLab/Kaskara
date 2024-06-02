# https://stackoverflow.com/questions/40431161/clang-tool-cannot-find-required-libraries-on-ubuntu-16-10
FROM christimperley/llvm18 as cpp

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
# -DKASKARA_BUILD_STATIC=TRUE \
# -DBUILD_SHARED_LIBS=FALSE \
# TODO: -l:libm.a

#      -DCMAKE_PREFIX_PATH=/opt/kaskara \
ADD . /tmp/kaskara
RUN mkdir /tmp/kaskara/build \
 && cd /tmp/kaskara/build \
 && cmake \
      -DCMAKE_INSTALL_PREFIX=/opt/kaskara \
      -DCMAKE_CXX_COMPILER=clang++ \
      -DCMAKE_CXX_FLAGS="-fuse-ld=lld -stdlib=libc++ -static-libstdc++ -fPIC" \
      -DCMAKE_POSITION_INDEPENDENT_CODE=TRUE \
      -DCMAKE_LINKER=ld.lld \
      .. \
 && make -j8 \
 && make install

# FIXME this should be part of the CMake install
RUN mkdir -p /opt/kaskara/clang \
 && cp -r /opt/llvm/lib/clang/*/include/* /opt/kaskara/clang

FROM ubuntu:22.04 as minimal
COPY --from=cpp /opt/kaskara /opt/kaskara
COPY scripts /opt/kaskara/scripts
WORKDIR /opt/kaskara
ENV PATH "/opt/kaskara/scripts:${PATH}"
