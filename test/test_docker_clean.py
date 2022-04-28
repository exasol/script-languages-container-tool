import unittest

import utils as exaslct_utils


class DockerClean(unittest.TestCase):

    def setUp(self):
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(self, exaslct_utils.EXASLCT_DEFAULT_BIN)

    def tearDown(self):
        try:
            self.test_environment.close()
        except Exception as e:
            print(e)

    def test_docker_clean_all_images(self):
        self.test_environment.clean_all_images()


if __name__ == '__main__':
    unittest.main()
