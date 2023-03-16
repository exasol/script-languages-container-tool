FROM opensuse/archive:42.1

RUN zypper --non-interactive install tar curl || true
RUN curl  https://download.docker.com/linux/static/stable/x86_64/docker-23.0.1.tgz | tar -xz
RUN mv docker/docker /usr/sbin

COPY run_ci_test_within_docker_bash_below_4.4.sh /run_ci_test_within_docker_bash_below_4.4.sh
ENTRYPOINT ["/run_ci_test_within_docker_bash_below_4.4.sh"]
