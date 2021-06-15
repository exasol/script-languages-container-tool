import unittest

import utils as exaslct_utils


class RunDBTestDockerPassThroughTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(self, exaslct_utils.EXASLCT_DEFAULT_BIN)
        self.test_environment.clean_images()

    def tearDown(self):
        try:
            self.test_environment.close()
        except Exception as e:
            print(e)

    def test_docker_test_environment(self):
        command = f"{self.test_environment.executable} run-db-test --test-file docker_environment_test.py"
        self.test_environment.run_command(command, track_task_dependencies=True)


if __name__ == '__main__':
    unittest.main()
