import unittest

import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.testing import utils  # type: ignore


class GenerateLanguageActivationTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(
            self, exaslct_utils.EXASLCT_DEFAULT_BIN
        )

    def tearDown(self):
        utils.close_environments(self.test_environment)

    def test_generate_with_path_in_bucket(self):
        command = (
            f"{self.test_environment.executable} generate-language-activation --bucketfs-name bfsdefault "
            f"--bucket-name default --path-in-bucket path --container-name container"
        )
        completed_process = self.test_environment.run_command(
            command,
            use_docker_repository=False,
            use_output_directory=False,
            capture_output=True,
        )
        self.assertIn(
            "ALTER SESSION SET SCRIPT_LANGUAGES='PYTHON3_TEST="
            "localzmq+protobuf:///bfsdefault/default/path/container?lang="
            "python#buckets/bfsdefault/default/path/container/exaudf/exaudfclient_py3';",
            completed_process.stdout.decode("UTF-8"),
        )

    def test_generate_without_path_in_bucket(self):
        command = (
            f"{self.test_environment.executable} generate-language-activation --bucketfs-name bfsdefault "
            f"--bucket-name default --container-name container"
        )
        completed_process = self.test_environment.run_command(
            command,
            use_docker_repository=False,
            use_output_directory=False,
            capture_output=True,
        )
        self.assertIn(
            "ALTER SESSION SET SCRIPT_LANGUAGES='PYTHON3_TEST="
            "localzmq+protobuf:///bfsdefault/default/container?lang="
            "python#buckets/bfsdefault/default/container/exaudf/exaudfclient_py3';",
            completed_process.stdout.decode("UTF-8"),
        )


if __name__ == "__main__":
    unittest.main()
