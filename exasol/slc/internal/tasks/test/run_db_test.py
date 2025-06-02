# pylint: disable=no-member

from collections import namedtuple
from io import StringIO
from pathlib import Path
from typing import Optional, Tuple

import docker.models.containers
import luigi
from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorBaseTask,
)
from exasol_integration_test_docker_environment.lib.base.frozendict_to_dict import (
    FrozenDictToDict,
)
from exasol_integration_test_docker_environment.lib.base.json_pickle_target import (
    JsonPickleTarget,
)
from exasol_integration_test_docker_environment.lib.models.config.docker_config import (
    source_docker_repository_config,
    target_docker_repository_config,
)
from exasol_integration_test_docker_environment.lib.models.config.log_config import (
    WriteLogFilesToConsole,
    log_config,
)
from exasol_integration_test_docker_environment.lib.models.data.container_info import (
    ContainerInfo,
)
from exasol_integration_test_docker_environment.lib.models.data.database_credentials import (
    DatabaseCredentialsParameter,
)
from exasol_integration_test_docker_environment.lib.models.data.database_info import (
    DatabaseInfo,
)
from exasol_integration_test_docker_environment.lib.models.data.environment_type import (
    EnvironmentType,
)

from exasol.slc.internal.tasks.test.run_db_tests_parameter import RunDBTestParameter
from exasol.slc.internal.utils.docker_utils import exec_run_and_write_to_stream
from exasol.slc.models.run_db_test_result import RunDBTestResult

DockerCredentials = namedtuple("DockerCredentials", "username password")


class DockerCommandException(Exception):
    """
    Executing a special command inside the TestContainer failed.
    """


class RunDBTest(FlavorBaseTask, RunDBTestParameter, DatabaseCredentialsParameter):
    test_file: str = luigi.Parameter()  # type: ignore

    def extend_output_path(self) -> tuple[str, ...]:
        test_file_name = Path(self.test_file).name
        extension = []
        if self.language is not None:
            extension.append(self.language)
        extension.append(test_file_name)
        return tuple(self.caller_output_path) + tuple(extension)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._test_container_info: Optional[ContainerInfo] = (
            self.test_environment_info.test_container_info
        )
        self._database_info: DatabaseInfo = self.test_environment_info.database_info

    def _run_command(
        self,
        docker_client: docker.client,
        container: docker.models.containers.Container,
        command: str,
    ) -> str:
        file = StringIO()
        exit_code = exec_run_and_write_to_stream(
            docker_client, container, command, file, {}
        )
        if exit_code != 0:
            raise DockerCommandException(f"Command returned {exit_code}: {command}")
        return file.getvalue().strip()

    def run_task(self) -> None:
        self.logger.info("Running db tests")
        assert self._test_container_info is not None
        with self._get_docker_client() as docker_client:
            test_container = docker_client.containers.get(
                self._test_container_info.container_name
            )
            odbc_driver = self._run_command(
                docker_client,
                test_container,
                r"find /downloads/ODBC -name libexaodbc\*.so",
            )
            bash_cmd = self.generate_test_command(odbc_driver)
            test_output_file = self.get_log_path().joinpath("test_output")
            exit_code = self.run_test_command(
                docker_client, bash_cmd, test_container, test_output_file
            )
            self.handle_test_result(exit_code, test_output_file)

    @staticmethod
    def read_test_output_file(test_output_file: Path) -> str:
        with open(test_output_file) as f:
            return f.read()

    def handle_test_result(self, exit_code: int, test_output_file: Path) -> None:
        is_test_ok = exit_code == 0
        if log_config().write_log_files_to_console == WriteLogFilesToConsole.all:
            self.logger.info(
                "Test results for db tests\n%s"
                % self.read_test_output_file(test_output_file)
            )
        if (
            log_config().write_log_files_to_console == WriteLogFilesToConsole.only_error
            and not is_test_ok
        ):
            self.logger.error(
                "Test results for db tests\n%s"
                % self.read_test_output_file(test_output_file)
            )

        result = RunDBTestResult(
            test_file=str(self.test_file),
            language=str(self.language),
            is_test_ok=is_test_ok,
            test_output_file=test_output_file,
        )
        JsonPickleTarget(self.get_output_path().joinpath("test_result.json")).write(
            result, 4
        )
        self.return_object(result)

    @staticmethod
    def _get_docker_credentials() -> Optional[DockerCredentials]:

        if (
            source_docker_repository_config().username is not None
            and source_docker_repository_config().password is not None
        ):
            return DockerCredentials(
                source_docker_repository_config().username,
                source_docker_repository_config().password,
            )
        if (
            target_docker_repository_config().username is not None
            and target_docker_repository_config().password is not None
        ):
            return DockerCredentials(
                target_docker_repository_config().username,
                target_docker_repository_config().password,
            )
        return None

    def run_test_command(
        self,
        docker_client: docker.client,
        bash_cmd: str,
        test_container: docker.models.containers.Container,
        test_output_file: Path,
    ) -> int:
        environment = FrozenDictToDict().convert(self.test_environment_vars)
        docker_credentials = self.__class__._get_docker_credentials()
        if docker_credentials is not None:
            environment["DOCKER_USERNAME"] = docker_credentials.username
            environment["DOCKER_PASSWORD"] = "***"

        env_type: str = (
            self.test_environment_info.type.name
            if isinstance(self.test_environment_info.type, EnvironmentType)
            else self.test_environment_info.type
        )
        environment["TEST_ENVIRONMENT_TYPE"] = env_type
        environment["TEST_ENVIRONMENT_NAME"] = self.test_environment_info.name
        environment["TEST_DOCKER_NETWORK_NAME"] = (
            self.test_environment_info.network_info.network_name
        )
        if self.test_environment_info.database_info.container_info is not None:
            environment["TEST_DOCKER_DB_CONTAINER_NAME"] = (
                self.test_environment_info.database_info.container_info.container_name
            )

        self.logger.info(f"Writing test-log to {test_output_file}")
        test_output = (
            "command: " + bash_cmd + "\n" + "environment: " + str(environment) + "\n"
        )
        with test_output_file.open("w") as file:
            file.write(test_output)
            if docker_credentials is not None:
                environment["DOCKER_PASSWORD"] = docker_credentials.password
            exit_code = exec_run_and_write_to_stream(
                docker_client, test_container, bash_cmd, file, environment
            )
        return exit_code

    def generate_test_command(self, odbc_driver: str) -> str:
        def quote(s):
            return f"'{s}'"

        def command_line():
            host = self._database_info.host
            port = self._database_info.ports.database
            yield from [
                "cd /tests/test/;",
                "python3",
                quote(self.test_file),
                "--server",
                quote(f"{host}:{port}"),
                "--user",
                quote(self.db_user),
                "--password",
                quote(self.db_password),
                "--script-languages",
                quote(self.language_definition),
                "--lang-path",
                "/tests/lang",
                f"--loglevel={self.test_log_level}",
                f"--driver={odbc_driver}",
                "--jdbc-path",
                "/downloads/JDBC/exajdbc.jar",
            ]
            if self.language is not None:
                yield from ["--lang", self.language]
            yield from self.test_restrictions  # pylint: disable=not-an-iterable

        command = " ".join([e for e in command_line()])
        return f'bash -c "{command}"'
