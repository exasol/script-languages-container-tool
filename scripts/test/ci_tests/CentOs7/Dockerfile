FROM centos:7

# latest https://download.docker.com/linux/centos/7/x86_64/stable/Packages/docker-ce-26.1.4-1.el7.x86_64.rpm
# before https://download.docker.com/linux/centos/7/x86_64/stable/Packages/docker-ce-17.06.0.ce-1.el7.centos.x86_64.rpm 

RUN yum install -y htop atop mc
RUN yum install -y \
    https://download.docker.com/linux/centos/7/x86_64/stable/Packages/docker-ce-18.03.1.ce-1.el7.centos.x86_64.rpm && \
    yum clean all

COPY run_ci_test_within_docker_bash_below_4.4.sh /run_ci_test_within_docker_bash_below_4.4.sh
ENTRYPOINT ["/run_ci_test_within_docker_bash_below_4.4.sh"]
