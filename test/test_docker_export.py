import os
import tarfile
import unittest
from pathlib import Path

import docker
import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.testing import utils

from exasol.slc.internal.utils.docker_utils import find_images_by_tag


class DockerExportTest(unittest.TestCase):
    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(
            self, exaslct_utils.EXASLCT_DEFAULT_BIN
        )
        self.export_path = self.test_environment.temp_dir + "/export_dir"
        self.docker_client = docker.from_env()
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
                [
                    "test-flavor_release_x64.tar.gz",
                    "test-flavor_release_x64.tar.gz.sha512sum",
                ]
            ),
            f"Did not found saved files for repository {self.test_environment.repository_name} "
            f"in list {exported_files}",
        )

        # Verify that "exasol-manifest.json" is the last file in the Tar archive
        with tarfile.open(
            os.path.join(self.export_path, "test-flavor_release_x64.tar.gz"), "r:*"
        ) as tf:
            tf_members = tf.getmembers()
            last_tf_member = tf_members[-1]
            assert last_tf_member.name == "exasol-manifest.json"
            assert last_tf_member.path == "exasol-manifest.json"
        images = find_images_by_tag(
            self.docker_client,
            lambda tag: tag.startswith(self.test_environment.repository_name),
        )
        self.assertGreater(len(images), 0, "Images for repository were not found.")

    def test_docker_export_with_image_cleanup(self):
        command = f"{self.test_environment.executable} export --export-path {self.export_path} --cleanup-docker-images"
        self.test_environment.run_command(command, track_task_dependencies=True)
        exported_files = os.listdir(self.export_path)
        self.assertEqual(
            sorted(list(exported_files)),
            sorted(
                [
                    "test-flavor_release_x64_.tar.gz",
                    "test-flavor_release_x64_.tar.gz.sha512sum",
                ]
            ),
            f"Did not found saved files for repository {self.test_environment.repository_name} "
            f"in list {exported_files}",
        )

        # Verify that "exasol-manifest.json" is the last file in the Tar archive
        with tarfile.open(
            os.path.join(self.export_path, "test-flavor_release_x64_.tar.gz"), "r:*"
        ) as tf:
            tf_members = tf.getmembers()
            last_tf_member = tf_members[-1]
            assert last_tf_member.name == "exasol-manifest.json"
            assert last_tf_member.path == "exasol-manifest.json"
        images = find_images_by_tag(
            self.docker_client,
            lambda tag: tag.startswith(self.test_environment.repository_name),
        )
        self.assertTrue(len(images) == 0, "Images for repository were not deleted.")

    def test_docker_export_with_symlink_for_export_path(self):
        command = (
            f"{self.test_environment.executable} export --export-path {self.export_path} "
            f"--use-symlink-for-export-path"
        )
        self.test_environment.run_command(command, track_task_dependencies=True)
        exported_file = Path(self.export_path) / "test-flavor_release_x64_.tar.gz"
        self.assertTrue(exported_file.is_symlink())
        linked_target = Path(os.readlink(exported_file))
        self.assertTrue(linked_target.is_absolute())
        self.assertEqual(
            linked_target.parent,
            Path(self.test_environment.temp_dir).joinpath("cache", "exports"),
        )
        self.assertEqual(exported_file.resolve(), linked_target.resolve())

        with tarfile.open(exported_file, "r:*") as tf:
            tf_members = tf.getmembers()
            last_tf_member = tf_members[-1]
            assert last_tf_member.name == "exasol-manifest.json"
            assert last_tf_member.path == "exasol-manifest.json"

        images = find_images_by_tag(
            self.docker_client,
            lambda tag: tag.startswith(self.test_environment.repository_name),
        )
        self.assertTrue(len(images) > 0, "Images for repository were not found.")


if __name__ == "__main__":
    unittest.main()
