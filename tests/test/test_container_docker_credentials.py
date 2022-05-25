#!/usr/bin/env python3
import os
import sys

import docker
from exasol_python_test_framework import udf
from exasol_python_test_framework import docker_db_environment


class TestContainerEnvironmentTest(udf.TestCase):

    @udf.skipIfNot(docker_db_environment.is_available, reason="This test requires a docker-db environment")
    def test_check_docker_credentials(self):
        docker_user = os.getenv("DOCKER_USERNAME")
        docker_password = os.getenv("DOCKER_PASSWORD")
        self.assertTrue(len(docker_user) > 0)
        self.assertTrue(len(docker_password) > 0)
        client = docker.from_env()
        client.login(username=docker_user, password=docker_password)


if __name__ == '__main__':
    udf.main()
