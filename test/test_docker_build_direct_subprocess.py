import os
import sys
import tempfile

import docker
from exasol_integration_test_docker_environment.lib.base.luigi_log_config import LOG_ENV_VARIABLE_NAME

from exasol_script_languages_container_tool.cli.commands import build, clean_flavor_images

from exasol_script_languages_container_tool.lib.utils.docker_utils import find_images_by_tag
from click.testing import CliRunner

import utils as exaslct_utils
from exasol_integration_test_docker_environment.testing import exaslct_test_environment


class DockerBuildTest(object):

    def __init__(self):
        self.test_environment = exaslct_test_environment.ExaslctTestEnvironment(self,
                                                                                exaslct_utils.EXASLCT_DEFAULT_BIN)
        self.docker_client = docker.from_env()
        self.runner = CliRunner()

    def shutdown(self):
        self.docker_client.close()

    @property
    def number_iterations(self):
        return 5

    def _clean_images(self):
        self.runner.invoke(clean_flavor_images,
                           f"{self.test_environment.flavor_path_argument} "
                           f"{self.test_environment.clean_docker_repository_arguments}")

    def run_test_docker_build(self):
        """
        Test that executing any exaslct task multiple times within the same Python process,
        does not have any side effects and that log file is on expected location
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ[LOG_ENV_VARIABLE_NAME] = f"{temp_dir}/main.log"

            self._clean_images()
            for i in range(self.number_iterations):
                print(f"Execute build run: {i}.")
                result = self.runner.invoke(build, f"{self.test_environment.flavor_path_argument} "
                                                   f"{self.test_environment.docker_repository_arguments}")
                print(result.stdout)
                assert result.exit_code == 0
                assert "Logging error" not in result.stdout
            images = find_images_by_tag(self.docker_client,
                                        lambda tag: tag.startswith(self.test_environment.repository_name))
            assert len(images) > 0
            self._clean_images()

            with open(os.getenv(LOG_ENV_VARIABLE_NAME), "r") as f:
                log_content = f.read()
                #Verify that for two clean command and n build commands the luigi tasks succeeded.
                assert log_content.count("This progress looks :) because there were no "
                                         "failed tasks or missing dependencies") == self.number_iterations + 2



if __name__ == '__main__':
    test_type = sys.argv[1]

    runner = DockerBuildTest()

    if test_type == "run_test_docker_build":
        runner.run_test_docker_build()
    else:
        raise ValueError("Invalid test!")

    runner.shutdown()
