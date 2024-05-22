FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

COPY ext/01_nodoc /etc/dpkg/dpkg.cfg.d/01_nodoc

RUN apt-get -y update && \
    apt-get -y install --no-install-recommends\
        ca-certificates \
        locales \
        python3.10-venv \
        git \
        bash \
        curl && \
    locale-gen en_US.UTF-8 && \
    update-locale LC_ALL=en_US.UTF-8 && \
    apt-get -y clean && \
    apt-get -y autoremove && \
    ldconfig

RUN curl https://bootstrap.pypa.io/get-pip.py | python3.10

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN mkdir /script-languages-container-tool
COPY exasol_script_languages_container_tool /script-languages-container-tool/exasol_script_languages_container_tool
COPY poetry.lock /script-languages-container-tool/poetry.lock
COPY pyproject.toml /script-languages-container-tool/pyproject.toml
COPY LICENSE /script-languages-container-tool/LICENSE
COPY README.md /script-languages-container-tool/README.md

WORKDIR /script-languages-container-tool
RUN python3.10 -m pip install .

RUN mkdir -p runner
COPY docker_runner/ /docker_runner
