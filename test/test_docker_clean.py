import unittest

import utils as exaslct_utils  # type: ignore # pylint: disable=import-error


class DockerClean(unittest.TestCase):

    def setUp(self):
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(
            self, exaslct_utils.EXASLCT_DEFAULT_BIN
        )

    def tearDown(self):
        try:
            self.test_environment.close()
        except Exception as e:
            print(e)

    def test_docker_clean_all_images(self):
        command = f"{self.test_environment.executable} clean-all-images"
        self.test_environment.run_command(command, use_flavor_path=False, clean=True)


if __name__ == "__main__":
    unittest.main()
