# https://stackoverflow.com/questions/40431161/clang-tool-cannot-find-required-libraries-on-ubuntu-16-10
FROM christimperley/clang as bond

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
RUN cd /usr/include && \
    wget https://github.com/nlohmann/json/releases/download/v2.1.1/json.hpp

## portable, internal gcov
#RUN apt-get install -y flex && \
#    cd /tmp && \
#    wget -q https://github.com/gcc-mirror/gcc/archive/gcc-6_3_0-release.tar.gz && \
#    tar -xf gcc-6_3_0-release.tar.gz && \
#    mv gcc-gcc-6_3_0-release gcc && \
#    cd gcc && \
#    ./contrib/download_prerequisites && \
#    mkdir -p /tmp/gcc-build && \
#    cd /tmp/gcc-build && \
#    /tmp/gcc/configure --prefix=/opt/gcov --enable-languages=c,c++ --disable-multilib && \
#    make -j8 && \
#    make install -j8 && \
#    cd / && \
#    rm -rf /tmp/*
#RUN mv /opt/gcov/bin/gcov /opt/gcov/gcov && \
#    rm -rf /opt/gcov/bin /opt/gcov/include /opt/gcov/lib* /opt/gcov/share
#VOLUME /opt/gcov

ADD . /tmp/bond
RUN mkdir /tmp/bond/build && \
    cd /tmp/bond/build && \
    cmake .. && \
    make -j $(nproc)

# add clang C files
FROM cmumars/cp2:base as test
RUN mkdir -p /opt/bond
COPY --from=bond /tmp/bond/build/src/bond /opt/bond/bond
COPY --from=bond /usr/local/lib/clang/5.0.0/include /opt/bond/clang
ENV CLANG_INCLUDE_PATH /opt/bond/clang
ENV C_INCLUDE_PATH "${C_INCLUDE_PATH}:${CLANG_INCLUDE_PATH}"
ENV CPLUS_INCLUDE_PATH "${CPLUS_INCLUDE_PATH}:${CLANG_INCLUDE_PATH}"
COPY test.sh .
