import pathlib
from typing import Any, Generator, Optional

import luigi
from docker.models.containers import ExecResult
from exasol_integration_test_docker_environment.abstract_method_exception import (
    AbstractMethodException,
)
from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask
from exasol_integration_test_docker_environment.lib.base.db_os_executor import (
    DbOsExecFactory,
    DbOsExecutor,
    DockerClientFactory,
    DockerExecFactory,
    SshExecFactory,
)
from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorBaseTask,
)
from exasol_integration_test_docker_environment.lib.models.data.database_credentials import (
    DatabaseCredentials,
)
from exasol_integration_test_docker_environment.lib.models.data.database_info import (
    DatabaseInfo,
)
from exasol_integration_test_docker_environment.lib.models.data.environment_info import (
    EnvironmentInfo,
)
from exasol_integration_test_docker_environment.lib.models.data.environment_type import (
    EnvironmentType,
)
from exasol_integration_test_docker_environment.lib.test_environment.parameter.docker_db_test_environment_parameter import (  # pylint: disable=line-too-long
    DbOsAccess,
)
from exasol_integration_test_docker_environment.lib.test_environment.parameter.spawn_test_environment_parameter import (  # pylint: disable=line-too-long
    SpawnTestEnvironmentParameter,
)
from exasol_integration_test_docker_environment.lib.test_environment.spawn_test_environment import (
    SpawnTestEnvironment,
)

from exasol.slc.internal.tasks.test.populate_test_engine import PopulateTestEngine
from exasol.slc.internal.tasks.test.run_db_tests_in_test_config import (
    RunDBTestsInTestConfig,
)
from exasol.slc.internal.tasks.test.run_db_tests_parameter import (
    RunDBTestsInTestConfigParameter,
)
from exasol.slc.internal.tasks.upload.language_definition import LanguageDefinition
from exasol.slc.models.run_db_test_result import RunDBTestsInTestConfigResult


class DummyExecutor(DbOsExecutor):

    def exec(self, cmd: str) -> ExecResult:
        raise RuntimeError("Not supposed to be called.")

    def prepare(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        pass


class DummyExecFactory(DbOsExecFactory):
    def executor(self) -> DbOsExecutor:
        return DummyExecutor()


class TestRunnerDBTestBaseTask(
    FlavorBaseTask, SpawnTestEnvironmentParameter, RunDBTestsInTestConfigParameter
):
    reuse_uploaded_container: bool = luigi.BoolParameter(False, significant=False)  # type: ignore
    release_goal: str = luigi.Parameter()  # type: ignore

    def __init__(self, *args, **kwargs) -> None:
        self.test_environment_info: Optional[EnvironmentInfo] = None
        super().__init__(*args, **kwargs)

    def register_spawn_test_environment(self) -> None:
        test_environment_name = f"""{self.get_flavor_name()}_{self.release_goal}"""
        spawn_test_environment_task = self.create_child_task_with_common_params(
            SpawnTestEnvironment, environment_name=test_environment_name
        )
        self._test_environment_info_future = self.register_dependency(
            spawn_test_environment_task
        )

    def run_task(self) -> Generator[BaseTask, None, None]:
        raise AbstractMethodException()

    def _executor_factory(self, database_info: DatabaseInfo) -> DbOsExecFactory:

        if self.db_os_access == DbOsAccess.SSH:
            return SshExecFactory.from_database_info(database_info)
        client_factory = DockerClientFactory(timeout=100000)
        if database_info.container_info is not None:
            return DockerExecFactory(
                database_info.container_info.container_name, client_factory
            )
        return DummyExecFactory()

    def populate_test_engine_data(
        self,
        test_environment_info: EnvironmentInfo,
        database_credentials: DatabaseCredentials,
    ) -> Generator[PopulateTestEngine, None, None]:
        assert self.test_environment_info is not None
        reuse = (
            self.reuse_database_setup
            and self.test_environment_info.database_info.reused
        )
        if not reuse:
            task = self.create_child_task(
                PopulateTestEngine,
                test_environment_info=test_environment_info,
                environment_name=self.test_environment_info.name,
                db_user=database_credentials.db_user,
                db_password=database_credentials.db_password,
                bucketfs_write_password=database_credentials.bucketfs_write_password,
            )
            yield from self.run_dependencies(task)

    def get_database_credentials(self) -> DatabaseCredentials:
        if self.environment_type == EnvironmentType.external_db:
            return DatabaseCredentials(
                db_user=self.external_exasol_db_user,
                db_password=self.external_exasol_db_password,
                bucketfs_write_password=self.external_exasol_bucketfs_write_password,
            )
        else:
            return DatabaseCredentials(
                db_user=SpawnTestEnvironment.DEFAULT_DB_USER,
                db_password=SpawnTestEnvironment.DEFAULT_DATABASE_PASSWORD,
                bucketfs_write_password=SpawnTestEnvironment.DEFAULT_BUCKETFS_WRITE_PASSWORD,
            )

    def _get_uploaded_container_name(self) -> str:
        raise AbstractMethodException()

    def run_test(
        self, test_environment_info: EnvironmentInfo, uploaded_container_name: str
    ) -> Generator[RunDBTestsInTestConfig, Any, RunDBTestsInTestConfigResult]:
        test_config = self.read_test_config()
        generic_language_tests = self.get_generic_language_tests(test_config)
        test_folders = self.get_test_folders(test_config)
        database_credentials = self.get_database_credentials()
        # "myudfs/containers/" + self.export_info.name + ".tar.gz"
        language_definition = LanguageDefinition(
            release_name=uploaded_container_name,
            flavor_path=self.flavor_path,  # type: ignore
            bucket_name="myudfs",
            bucketfs_name="bfsdefault",
            path_in_bucket="",
            add_missing_builtin=True,
        )
        task = self.create_child_task_with_common_params(
            RunDBTestsInTestConfig,
            test_environment_info=test_environment_info,
            generic_language_tests=generic_language_tests,
            test_folders=test_folders,
            language_definition=language_definition.generate_definition(),
            db_user=database_credentials.db_user,
            db_password=database_credentials.db_password,
            bucketfs_write_password=database_credentials.bucketfs_write_password,
        )
        test_output_future: Any = yield from self.run_dependencies(task)
        test_output: RunDBTestsInTestConfigResult = self.get_values_from_future(
            test_output_future
        )  # type: ignore
        assert isinstance(test_output, RunDBTestsInTestConfigResult)
        return test_output

    @staticmethod
    def get_result_status(status):
        result_status = "OK"
        for line in status.split("\n"):
            if line != "":
                if line.endswith("FAILED"):
                    result_status = "FAILED"
                    break
        return result_status

    def get_test_folders(self, test_config):
        test_folders = []
        if test_config["test_folders"] != "":
            test_folders = test_config["test_folders"].split(" ")
        if self.tests_specified_in_parameters():
            test_folders = self.test_folders
        return test_folders

    def tests_specified_in_parameters(self):
        return (
            len(self.generic_language_tests) != 0
            or len(self.test_folders) != 0
            or len(self.test_files) != 0
        )

    def get_generic_language_tests(self, test_config):
        generic_language_tests = []
        if test_config["generic_language_tests"] != "":
            generic_language_tests = test_config["generic_language_tests"].split(" ")
        if self.tests_specified_in_parameters():
            generic_language_tests = self.generic_language_tests
        return generic_language_tests

    def read_test_config(self):
        with pathlib.Path(self.flavor_path).joinpath("flavor_base").joinpath(
            "testconfig"
        ).open("r") as file:
            test_config_str = file.read()
            test_config = {}
            for line in test_config_str.splitlines():
                if not line.startswith("#") and not line == "":
                    split = line.split("=")
                    key = split[0]
                    value = "=".join(split[1:])
                    test_config[key] = value
        return test_config
