# https://stackoverflow.com/questions/40431161/clang-tool-cannot-find-required-libraries-on-ubuntu-16-10
FROM christimperley/clang as kaskara

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
 && cmake .. \
 && make -j4 \
 && make install \
 && rm -rf /tmp/*

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

# add scripts
ADD scripts /opt/kaskara/scripts
ADD . /tmp/kaskara
RUN mkdir /tmp/kaskara/build && \
    cd /tmp/kaskara/build && \
    cmake .. && \
    make -j $(nproc)

# add clang C files
FROM cmumars/cp2:backup as test
# FROM cmumars/cp2:base as test
RUN mkdir -p /opt/kaskara
COPY --from=kaskara /opt/kaskara/scripts /opt/kaskara/scripts
COPY --from=kaskara /tmp/kaskara/build/cpp/kaskara-loop-finder /opt/kaskara/bin/kaskara-loop-finder
COPY --from=kaskara /tmp/kaskara/build/cpp/kaskara-function-scanner /opt/kaskara/bin/kaskara-function-scanner
COPY --from=kaskara /usr/local/lib/clang/5.0.0/include /opt/kaskara/clang
ENV PATH "/opt/kaskara/scripts:${PATH}"
COPY test.sh .
