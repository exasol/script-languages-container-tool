from pathlib import Path

from exasol_integration_test_docker_environment.testing import exaslct_test_environment

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

