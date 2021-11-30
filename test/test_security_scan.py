import unittest

import utils as exaslct_utils
from exasol_integration_test_docker_environment.testing import utils


class DockerSecurityScanTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(self, exaslct_utils.EXASLCT_DEFAULT_BIN)
        self.test_environment.clean_images()

    def tearDown(self):
        utils.close_environments(self.test_environment)

    def test_docker_build(self):
        command = f"{self.test_environment.executable} security-scan"
        completed_process = self.test_environment.run_command(command,
                                                              track_task_dependencies=True, capture_output=True)
        output = completed_process.stdout.decode("UTF-8")
        self.assertIn("============ START SECURITY SCAN REPORT - ", output)
        self.assertIn("running security scan", output)
        self.assertIn("============ END SECURITY SCAN REPORT - ", output)


if __name__ == '__main__':
    unittest.main()
