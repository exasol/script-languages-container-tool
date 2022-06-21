from collections import namedtuple
from pathlib import Path
from typing import Tuple, Optional

import docker.models.containers
import luigi
from exasol_integration_test_docker_environment.lib.config.docker_config import source_docker_repository_config, \
    target_docker_repository_config

from exasol_script_languages_container_tool.lib.tasks.test.run_db_test_result import RunDBTestResult
from exasol_script_languages_container_tool.lib.tasks.test.run_db_tests_parameter import RunDBTestParameter
from exasol_integration_test_docker_environment.lib.base.flavor_task import FlavorBaseTask
from exasol_integration_test_docker_environment.lib.base.frozendict_to_dict import FrozenDictToDict
from exasol_integration_test_docker_environment.lib.base.json_pickle_target import JsonPickleTarget
from exasol_integration_test_docker_environment.lib.data.database_credentials import DatabaseCredentialsParameter


class RunDBTest(FlavorBaseTask,
                RunDBTestParameter,
                DatabaseCredentialsParameter):
    test_file = luigi.Parameter()

    def extend_output_path(self):
        test_file_name = Path(self.test_file).name
        extension = []
        if self.language is not None:
            extension.append(self.language)
        extension.append(test_file_name)
        return self.caller_output_path + tuple(extension)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._test_container_info = self.test_environment_info.test_container_info
        self._database_info = self.test_environment_info.database_info

    def run_task(self):
        self.logger.info("Running db tests")
        with self._get_docker_client() as docker_client:
            test_container = docker_client.containers.get(self._test_container_info.container_name)
            bash_cmd = self.generate_test_command()
            environment, exit_code, output = self.run_test_command(docker_client, bash_cmd, test_container)
            self.handle_test_result(bash_cmd, environment, exit_code, output)

    def handle_test_result(self, bash_cmd: str, environment: luigi.DictParameter, exit_code: int, output: str) -> None:
        test_output = "command: " + bash_cmd + "\n" + \
                      "environment: " + str(environment) + "\n" + \
                      output
        is_test_ok = (exit_code == 0)
        test_output_file = self.get_log_path().joinpath("test_output")
        with test_output_file.open("w") as file:
            file.write(test_output)
        result = RunDBTestResult(
            test_file=self.test_file,
            language=self.language,
            is_test_ok=is_test_ok,
            test_output_file=test_output_file)
        JsonPickleTarget(self.get_output_path().joinpath("test_result.json")).write(result, 4)
        self.return_object(result)

    @staticmethod
    def _get_docker_credentials() -> Optional[namedtuple]:
        docker_credentials = namedtuple("DockerCredentials", "username password")
        if source_docker_repository_config().username is not None and \
                source_docker_repository_config().password is not None:
            return docker_credentials(source_docker_repository_config().username,
                                      source_docker_repository_config().password)
        if target_docker_repository_config().username is not None and \
                target_docker_repository_config().password is not None:
            return docker_credentials(target_docker_repository_config().username,
                                      target_docker_repository_config().password)
        return None

    def run_test_command(self, docker_client: docker.client, bash_cmd: str,
                         test_container: docker.models.containers.Container) -> Tuple[luigi.DictParameter, int, str]:
        environment = FrozenDictToDict().convert(self.test_environment_vars)
        docker_credentials = self.__class__._get_docker_credentials()
        if docker_credentials is not None:
            environment["DOCKER_USERNAME"] = docker_credentials.username
            environment["DOCKER_PASSWORD"] = docker_credentials.password
        environment["TEST_ENVIRONMENT_TYPE"] = self.test_environment_info.type.name
        environment["TEST_ENVIRONMENT_NAME"] = self.test_environment_info.name
        environment["TEST_DOCKER_NETWORK_NAME"] = self.test_environment_info.network_info.network_name
        if self.test_environment_info.database_info.container_info is not None:
            environment["TEST_DOCKER_DB_CONTAINER_NAME"] = \
                self.test_environment_info.database_info.container_info.container_name

        output = str()
        _id = docker_client.api.exec_create(container=test_container.id, cmd=bash_cmd, environment=environment)
        output_stream = docker_client.api.exec_start(_id, detach=False, stream=True)
        for output_chunk in output_stream:
            print(output_chunk.decode("utf-8"))
            output += output_chunk.decode("utf-8")
        ret = docker_client.api.exec_inspect(_id)
        exit_code = ret["ExitCode"]
        return environment, exit_code, output

    def generate_test_command(self) -> str:
        credentials = f"--user '{self.db_user}' --password '{self.db_password}'"
        log_level = f"--loglevel={self.test_log_level}"
        server = f"--server '{self._database_info.host}:{self._database_info.db_port}'"
        environment = "--driver=/downloads/ODBC/lib/linux/x86_64/libexaodbc-uo2214lv2.so  " \
                      "--jdbc-path /downloads/JDBC/exajdbc.jar"
        language_definition = f"--script-languages '{self.language_definition}'"
        language_path = f"--lang-path /tests/lang"
        language = ""
        if self.language is not None:
            language = "--lang %s" % self.language
        test_restrictions = " ".join(self.test_restrictions)
        test_file = f'"{self.test_file}"'
        args = " ".join([test_file,
                         server,
                         credentials,
                         language_definition,
                         language_path,
                         log_level,
                         environment,
                         language,
                         test_restrictions])
        cmd = f'cd /tests/test/; python3 {args}'
        bash_cmd = f"""bash -c "{cmd}" """
        return bash_cmd
