FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

COPY deps/01_nodoc /etc/dpkg/dpkg.cfg.d/01_nodoc

RUN apt-get -y update && \
    apt-get -y install \
        openjdk-11-jre \
        locales \
        python3.10-venv \
        python3-pip \
        unixodbc \
        unixodbc-dev \
        curl \
        git && \
    locale-gen en_US.UTF-8 && \
    update-locale LC_ALL=en_US.UTF-8 && \
    apt-get -y clean && \
    apt-get -y autoremove && \
    ldconfig

RUN curl -fsSL https://get.docker.com | bash

RUN mkdir -p downloads/ODBC downloads/JDBC downloads/EXAplus

# For latest drivers see https://downloads.exasol.com/clients-and-drivers/odbc

# old
# RUN curl -s https://exasol-script-languages-dependencies.s3.eu-central-1.amazonaws.com/EXASOL_ODBC-7.0.11.tar.gz | tar -C downloads/ODBC --strip-components 1 -zxf -
# RUN curl -s https://x-up.s3.amazonaws.com/7.x/7.1.14/EXASOL_JDBC-7.1.14.tar.gz | tar -C downloads/JDBC --strip-components 1 -zxf -
# RUN curl -s https://exasol-script-languages-dependencies.s3.eu-central-1.amazonaws.com/EXAplus-7.0.11.tar.gz | tar -C downloads/EXAplus --strip-components 1 -zxf -

RUN curl -s https://x-up.s3.amazonaws.com/7.x/24.1.1/Exasol_ODBC-24.1.1-Linux_x86_64.tar.gz  | tar -C downloads/ODBC --strip-components 2 -zxf -
RUN curl -s https://x-up.s3.amazonaws.com/7.x/24.1.1/Exasol_JDBC-24.1.1.tar.gz | tar -C downloads/JDBC --strip-components 2 -zxf -
RUN curl -s https://x-up.s3.amazonaws.com/7.x/24.1.1/EXAplus-24.1.1.tar.gz | tar -C downloads/EXAplus --strip-components 2 -zxf -
ENV EXAPLUS=/downloads/EXAplus/exaplus

COPY deps/requirements.txt requirements.txt
RUN python3.10 -m pip install pip -u
RUN python3.10 -m pip install -r requirements.txt
