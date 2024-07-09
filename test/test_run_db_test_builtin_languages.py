import unittest

import utils as exaslct_utils
from exasol_integration_test_docker_environment.testing import utils


class RunDBTestBuiltinLanguagesTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(self, exaslct_utils.EXASLCT_DEFAULT_BIN)
        self.test_environment.clean_images()

    def tearDown(self):
        utils.close_environments(self.test_environment)

    def test_builtin_languages(self):
        # optionally add "--reuse-test-environment" here
        command = " ".join([
            str(self.test_environment.executable),
            "run-db-test",
            "--test-file",
            "test_builtin_languages.py",
            exaslct_utils.get_full_test_container_folder_parameter(),
        ])
        self.test_environment.run_command(command, track_task_dependencies=True)


if __name__ == '__main__':
    unittest.main()
