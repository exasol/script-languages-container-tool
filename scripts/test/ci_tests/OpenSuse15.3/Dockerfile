FROM opensuse/leap:15.3

RUN zypper --non-interactive install docker

COPY run_ci_test_within_docker_bash_4.4_and_above.sh /run_ci_test_within_docker_bash_4.4_and_above.sh
ENTRYPOINT ["/run_ci_test_within_docker_bash_4.4_and_above.sh"]
