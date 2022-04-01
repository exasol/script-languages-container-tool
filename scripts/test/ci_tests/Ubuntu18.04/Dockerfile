FROM ubuntu:18.04

RUN apt-get -y update && \
    apt-get -y install \
    --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    curl \
    locales \
    gnupg \
    lsb-release && \
    locale-gen en_US.UTF-8 && \
    update-locale LC_ALL=en_US.UTF-8 && \
    apt-get -y clean && \
    apt-get -y autoremove


RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

RUN echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

RUN apt-get -y update && apt-get -y install --no-install-recommends \
    docker-ce docker-ce-cli containerd.io && \
    apt-get -y clean && \
    apt-get -y autoremove

COPY run_ci_test_within_docker_bash_4.4_and_above.sh /run_ci_test_within_docker_bash_4.4_and_above.sh
ENTRYPOINT ["/run_ci_test_within_docker_bash_4.4_and_above.sh"]
