FROM centos:7

RUN yum install -y htop atop mc
RUN yum install -y \
    https://download.docker.com/linux/centos/8/x86_64/stable/Packages/docker-ce-20.10.7-3.el8.x86_64.rpm \
    https://download.docker.com/linux/centos/8/x86_64/stable/Packages/docker-ce-rootless-extras-20.10.7-3.el8.x86_64.rpm \
    https://download.docker.com/linux/centos/8/x86_64/stable/Packages/docker-ce-cli-20.10.7-3.el8.x86_64.rpm \
    https://download.docker.com/linux/centos/8/x86_64/stable/Packages/containerd.io-1.4.6-3.1.el8.x86_64.rpm \
    https://download.docker.com/linux/centos/8/x86_64/stable/Packages/docker-scan-plugin-0.8.0-3.el8.x86_64.rpm

COPY run_ci_test_within_docker.sh /run_ci_test_within_docker.sh
ENTRYPOINT ["/run_ci_test_within_docker.sh"]