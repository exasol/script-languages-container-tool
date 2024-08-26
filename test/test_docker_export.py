import os
import tarfile
import unittest

import utils as exaslct_utils
from exasol_integration_test_docker_environment.testing import utils


class DockerExportTest(unittest.TestCase):
    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(
            self, exaslct_utils.EXASLCT_DEFAULT_BIN
        )
        self.export_path = self.test_environment.temp_dir + "/export_dir"
        self.test_environment.clean_images()

    def tearDown(self):
        utils.close_environments(self.test_environment)

    def test_docker_export(self):
        command = f"{self.test_environment.executable} export --export-path {self.export_path}"
        self.test_environment.run_command(command, track_task_dependencies=True)
        exported_files = os.listdir(self.export_path)
        self.assertEqual(
            sorted(list(exported_files)),
            sorted(
                ["test-flavor_release.tar.gz", "test-flavor_release.tar.gz.sha512sum"]
            ),
            f"Did not found saved files for repository {self.test_environment.repository_name} "
            f"in list {exported_files}",
        )

        # Verify that "exasol-manifest.json" is the last file in the Tar archive
        with tarfile.open(
            os.path.join(self.export_path, "test-flavor_release.tar.gz"), "r:*"
        ) as tf:
            tf_members = tf.getmembers()
            last_tf_member = tf_members[-1]
            assert last_tf_member.name == "exasol-manifest.json"
            assert last_tf_member.path == "exasol-manifest.json"


if __name__ == "__main__":
    unittest.main()
