FROM opensuse/archive:42.1

RUN zypper --non-interactive install docker || true # zypper fails with error code 106, because some repositories aren't reachable

COPY run_ci_test_within_docker_bash_below_4.4.sh /run_ci_test_within_docker_bash_below_4.4.sh
ENTRYPOINT ["/run_ci_test_within_docker_bash_below_4.4.sh"]
