#!/usr/bin/env python2.7
import os
import sys

sys.path.append(os.path.realpath(__file__ + '/../../lib'))

import udf
import docker_db_environment


class EmptyTest(udf.TestCase):

    @udf.skipIfNot(docker_db_environment.is_available, reason="This test requires a docker-db environment")
    def test_dummy(self):
        pass


if __name__ == '__main__':
    udf.main()

