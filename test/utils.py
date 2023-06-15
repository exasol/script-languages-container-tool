from pathlib import Path
from subprocess import CompletedProcess
from typing import List, Any, Dict

from exasol_integration_test_docker_environment.lib.data.test_container_content_description import \
    TestContainerContentDescription
from exasol_integration_test_docker_environment.testing import api_test_environment, exaslct_test_environment
from exasol_integration_test_docker_environment.testing.exaslct_docker_test_environment import \
    ExaslctDockerTestEnvironment
from exasol_integration_test_docker_environment.testing.spawned_test_environments import SpawnedTestEnvironments

from exasol_script_languages_container_tool.lib import api

RESOURCES_DIRECTORY = Path(__file__).parent / "resources"
TEST_CONTAINER_ROOT_DIRECTORY = RESOURCES_DIRECTORY / "test_container"
FLAVORS_ROOT_DIRECTORY = RESOURCES_DIRECTORY / "flavors"
EXASLCT_DEFAULT_BIN = Path(Path(__file__).parent.parent, "exaslct")


class ExaslctApiTestEnvironmentWithCleanup():

    def __init__(self, test_object, clean_images_at_close, name=None):
        self._itde_api_test_environement = api_test_environment.ApiTestEnvironment(
            test_object=test_object, name=name)
        self.clean_images_at_close = clean_images_at_close

    @property
    def docker_repository_name(self):
        return self._itde_api_test_environement.docker_repository_name

    @docker_repository_name.setter
    def docker_repository_name(self, value):
        self._itde_api_test_environement.docker_repository_name = value

    @property
    def test_object(self):
        return self._itde_api_test_environement.test_object

    @property
    def test_class(self):
        return self._itde_api_test_environement.test_class

    @property
    def name(self):
        return self._itde_api_test_environement.name

    @property
    def temp_dir(self):
        return self._itde_api_test_environement.temp_dir

    @property
    def output_dir(self):
        return self._itde_api_test_environement.temp_dir

    @property
    def task_dependency_dot_file(self):
        return self._itde_api_test_environement.task_dependency_dot_file

    def close(self):
        try:
            if self.clean_images_at_close:
                self.clean_all_images()
        except Exception as e:
            print(e)
        self._itde_api_test_environement.close()

    def clean_all_images(self):
        api.clean_all_images(docker_repository_name=self._itde_api_test_environement.docker_repository_name)

    def spawn_docker_test_environment_with_test_container(self, name: str,
                                                          test_container_content: TestContainerContentDescription,
                                                          additional_parameter: Dict[str, Any] = None) \
            -> ExaslctDockerTestEnvironment:
        return self._itde_api_test_environement.spawn_docker_test_environment_with_test_container(
            name=name,
            test_container_content=test_container_content,
            additional_parameter=additional_parameter
        )

    def spawn_docker_test_environment(self, name: str,
                                      additional_parameter: Dict[str, Any] = None) \
            -> ExaslctDockerTestEnvironment:
        return self._itde_api_test_environement.spawn_docker_test_environment(
            name=name, additional_parameter=additional_parameter
        )


class ExaslctTestEnvironmentWithCleanUp():

    def __init__(self,
                 test_object,
                 executable=EXASLCT_DEFAULT_BIN,
                 clean_images_at_close=True,
                 name=None,
                 flavor_path: Path = FLAVORS_ROOT_DIRECTORY / "test-flavor"):
        print("flavor_path", flavor_path)
        self._flavor_path = flavor_path
        self._clean_images_at_close = clean_images_at_close
        self._itde_cli_test_environment = exaslct_test_environment.ExaslctTestEnvironment(
            test_object=test_object,
            executable=executable,
            clean_images_at_close=False,
            name=name
        )

    @property
    def flavor_path(self):
        return self._flavor_path

    @property
    def executable(self):
        return self._itde_cli_test_environment.executable

    @property
    def test_object(self):
        return self._itde_cli_test_environment.test_object

    @property
    def test_class(self):
        return self._itde_cli_test_environment.test_class

    @property
    def name(self):
        return self._itde_cli_test_environment.name

    @property
    def temp_dir(self):
        return self._itde_cli_test_environment.temp_dir

    @property
    def repository_name(self):
        return self._itde_cli_test_environment.repository_name

    @repository_name.setter
    def repository_name(self, value):
        self._itde_cli_test_environment.repository_name = value

    def clean_images(self):
        self.run_command(f"{self.executable} clean-flavor-images", clean=True)

    def run_command(self,
                    command: str,
                    use_output_directory: bool = True,
                    use_docker_repository: bool = True,
                    use_flavor_path: bool = True,
                    track_task_dependencies: bool = False,
                    clean: bool = False,
                    capture_output: bool = False) -> CompletedProcess:
        if use_flavor_path:
            command = f"{command} --flavor-path {self.flavor_path} "
        return self._itde_cli_test_environment.run_command(command=command,
                                                           use_output_directory=use_output_directory,
                                                           use_flavor_path=False,
                                                           use_docker_repository=use_docker_repository,
                                                           track_task_dependencies=track_task_dependencies,
                                                           clean=clean,
                                                           capture_output=capture_output)

    def spawn_docker_test_environments(self, name: str, additional_parameter: List[str] = None) \
            -> SpawnedTestEnvironments:
        return self._itde_cli_test_environment.spawn_docker_test_environments(name, additional_parameter)

    def close(self):
        try:
            if self._clean_images_at_close:
                self.clean_all_images()
        except Exception as e:
            print(e)
        self._itde_cli_test_environment.close()

    def clean_all_images(self):
        self.run_command(f"{self.executable} clean-all-images", use_flavor_path=False, clean=True)


def get_full_test_container_folder_parameter() -> str:
    return f"--test-container-folder {get_full_test_container_folder()}"


def get_mock_test_container_folder_parameter() -> str:
    return f"--test-container-folder {get_mock_test_container_folder()}"


def get_full_test_container_folder() -> Path:
    path = TEST_CONTAINER_ROOT_DIRECTORY / "full"
    return path


def get_mock_test_container_folder() -> Path:
    path = TEST_CONTAINER_ROOT_DIRECTORY / "full"
    return path


def get_test_flavor() -> Path:
    path = FLAVORS_ROOT_DIRECTORY / "test-flavor"
    return path


def get_real_test_flavor() -> Path:
    path = FLAVORS_ROOT_DIRECTORY / "real-test-flavor"
    return path
