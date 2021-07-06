FROM centos:7

RUN yum install -y htop atop mc
RUN yum install -y \
    https://download.docker.com/linux/centos/7/x86_64/stable/Packages/docker-ce-17.06.0.ce-1.el7.centos.x86_64.rpm && \
    yum clean all

COPY run_ci_test_within_docker.sh /run_ci_test_within_docker.sh
ENTRYPOINT ["/run_ci_test_within_docker.sh"]