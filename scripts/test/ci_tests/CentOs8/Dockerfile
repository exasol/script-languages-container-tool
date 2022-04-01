FROM centos:8

# CentOS Linux 8 had reached the End Of Life (EOL), we need to use a different mirror (https://techglimpse.com/failed-metadata-repo-appstream-centos-8/)
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
RUN sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*
RUN yum update -y
RUN yum install -y  mc
RUN yum install -y \
    https://download.docker.com/linux/centos/8/x86_64/stable/Packages/docker-ce-20.10.7-3.el8.x86_64.rpm \
    https://download.docker.com/linux/centos/8/x86_64/stable/Packages/docker-ce-rootless-extras-20.10.7-3.el8.x86_64.rpm \
    https://download.docker.com/linux/centos/8/x86_64/stable/Packages/docker-ce-cli-20.10.7-3.el8.x86_64.rpm \
    https://download.docker.com/linux/centos/8/x86_64/stable/Packages/containerd.io-1.4.6-3.1.el8.x86_64.rpm \
    https://download.docker.com/linux/centos/8/x86_64/stable/Packages/docker-scan-plugin-0.8.0-3.el8.x86_64.rpm && \
    yum clean all

COPY run_ci_test_within_docker_bash_4.4_and_above.sh /run_ci_test_within_docker_bash_4.4_and_above.sh
ENTRYPOINT ["/run_ci_test_within_docker_bash_4.4_and_above.sh"]
