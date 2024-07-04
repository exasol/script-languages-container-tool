FROM centos:7

# see https://serverfault.com/questions/1161816/mirrorlist-centos-org-no-longer-resolve

RUN sed -i s/mirror.centos.org/vault.centos.org/g /etc/yum.repos.d/*.repo
RUN sed -i s/^#.*baseurl=http/baseurl=http/g /etc/yum.repos.d/*.repo
RUN sed -i s/^mirrorlist=http/#mirrorlist=http/g /etc/yum.repos.d/*.repo
RUN sed -i s/^mirrorlist=http/#mirrorlist=http/g /etc/yum.repos.d/*.repo

RUN yum install -y htop atop mc
RUN yum install -y \
    before https://download.docker.com/linux/centos/7/x86_64/stable/Packages/docker-ce-17.06.0.ce-1.el7.centos.x86_64.rpm && \
    yum clean all

COPY run_ci_test_within_docker_bash_below_4.4.sh /run_ci_test_within_docker_bash_below_4.4.sh
ENTRYPOINT ["/run_ci_test_within_docker_bash_below_4.4.sh"]
