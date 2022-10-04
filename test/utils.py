from pathlib import Path

from exasol_integration_test_docker_environment.testing import api_test_environment, exaslct_test_environment

from exasol_script_languages_container_tool.lib import api


class ExaslctApiTestEnvironmentWithCleanup(api_test_environment.ApiTestEnvironment):

    def __init__(self, test_object, clean_images_at_close):
        super().__init__(test_object)
        self.clean_images_at_close = clean_images_at_close

    def close(self):
        try:
            if self.clean_images_at_close:
                self.clean_all_images()
        except Exception as e:
            print(e)
        super().close()

    def clean_all_images(self):
        api.clean_all_images(docker_repository_name=self.docker_repository_name)


EXASLCT_DEFAULT_BIN = Path(Path(__file__).parent.parent, "exaslct")


class ExaslctTestEnvironmentWithCleanUp(exaslct_test_environment.ExaslctTestEnvironment):

    def close(self):
        try:
            if self.clean_images_at_close:
                self.clean_all_images()
        except Exception as e:
            print(e)
        super().close()

    def clean_all_images(self):
        self.run_command(f"{self.executable} clean-all-images", use_flavor_path=False, clean=True)


def get_test_container_folder_for_tests_parameter() -> str:
    path = Path(__file__).parent / "test_container"
    return f"--test-container-folder {path}"
