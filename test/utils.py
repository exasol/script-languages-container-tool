from pathlib import Path

import docker

from exasol_integration_test_docker_environment.testing import utils

EXASLCT_DEFAULT_BIN = Path(Path(__file__).parent.parent, "exaslct")


class ExaslctTestEnvironmentWithCleanUp(utils.ExaslctTestEnvironment):

    def close(self):
        try:
            if self.clean_images_at_close:
                self.clean_all_images()
        except Exception as e:
            print(e)
        super().close()

    def clean_all_images(self):
        self.run_command(f"{self.executable} clean-all-images", use_flavor_path=False, clean=True)

