FROM opensuse/leap:15.3

RUN zypper --non-interactive install docker

COPY run_ci_test_within_docker.sh /run_ci_test_within_docker.sh
ENTRYPOINT ["/run_ci_test_within_docker.sh"]