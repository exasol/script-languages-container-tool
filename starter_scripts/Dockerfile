FROM ubuntu:18.04

COPY ext/01_nodoc /etc/dpkg/dpkg.cfg.d/01_nodoc

RUN apt-get -y update && \
    apt-get -y install --no-install-recommends\
        ca-certificates \
        locales \
        python3-wheel \
        python3-setuptools \
        git \
        bash \
        curl && \
    locale-gen en_US.UTF-8 && \
    update-locale LC_ALL=en_US.UTF-8 && \
    apt-get -y clean && \
    apt-get -y autoremove && \
    ldconfig

RUN curl https://bootstrap.pypa.io/get-pip.py | python3

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
COPY . /script-languages-container-tool
WORKDIR /script-languages-container-tool
RUN python3 -m pip install .
