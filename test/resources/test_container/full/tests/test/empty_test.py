#!/usr/bin/env python3

from exasol_python_test_framework import docker_db_environment, udf


class EmptyTest(udf.TestCase):

    @udf.skipIfNot(
        docker_db_environment.is_available,
        reason="This test requires a docker-db environment",
    )
    def test_dummy(self):
        pass


if __name__ == "__main__":
    udf.main()
