import tarfile
import unittest

import docker
import export_test_utils
import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.testing import utils  # type: ignore

from exasol.slc import api
from exasol.slc.internal.utils.docker_utils import find_images_by_tag
from exasol.slc.models.compression_strategy import CompressionStrategy


class ApiDockerExportTest(unittest.TestCase):
    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctApiTestEnvironmentWithCleanup(
            self, True
        )
        self.export_path = self.test_environment.temp_dir + "/export_dir"
        self.docker_client = docker.from_env()
        self.test_environment.clean_all_images()

    def tearDown(self):
        utils.close_environments(self.test_environment)

    def test_docker_export(self):
        export_result = api.export(
            flavor_path=(str(exaslct_utils.get_test_flavor()),),
            export_path=self.export_path,
            target_docker_repository_name=self.test_environment.docker_repository_name,
            force_rebuild=True,
        )
        _, export_path = export_test_utils.assert_single_release_export(
            self,
            export_result,
            self.export_path,
            flavor_path=str(exaslct_utils.get_test_flavor()),
        )

        # Verify that "exasol-manifest.json" is the last file in the Tar archive
        with tarfile.open(export_path, "r:gz") as tf:
            tf_members = tf.getmembers()
            last_tf_member = tf_members[-1]
            assert last_tf_member.name == "exasol-manifest.json"
            assert last_tf_member.path == "exasol-manifest.json"
        images = find_images_by_tag(
            self.docker_client,
            lambda tag: tag.startswith(self.test_environment.docker_repository_name),
        )
        self.assertGreater(len(images), 0, "Images for repository were not found.")

    def test_docker_export_with_image_cleanup(self):
        export_result = api.export(
            flavor_path=(str(exaslct_utils.get_test_flavor()),),
            export_path=self.export_path,
            target_docker_repository_name=self.test_environment.docker_repository_name,
            cleanup_docker_images=True,
            force_rebuild=True,
        )
        _, export_path = export_test_utils.assert_single_release_export(
            self,
            export_result,
            self.export_path,
            flavor_path=str(exaslct_utils.get_test_flavor()),
        )

        # Verify that "exasol-manifest.json" is the last file in the Tar archive
        with tarfile.open(export_path, "r:gz") as tf:
            tf_members = tf.getmembers()
            last_tf_member = tf_members[-1]
            assert last_tf_member.name == "exasol-manifest.json"
            assert last_tf_member.path == "exasol-manifest.json"

        images = find_images_by_tag(
            self.docker_client,
            lambda tag: tag.startswith(self.test_environment.docker_repository_name),
        )
        self.assertEqual(len(images), 0, "Images for repository were not deleted.")

    def test_docker_export_uncompressed(self):
        export_result = api.export(
            flavor_path=(str(exaslct_utils.get_test_flavor()),),
            export_path=self.export_path,
            target_docker_repository_name=self.test_environment.docker_repository_name,
            compression_strategy=CompressionStrategy.NONE,
            force_rebuild=True,
        )
        _, export_path = export_test_utils.assert_single_release_export(
            self,
            export_result,
            self.export_path,
            flavor_path=str(exaslct_utils.get_test_flavor()),
        )
        self.assertEqual(export_path.suffix, ".tar")

        # Verify that "exasol-manifest.json" is the last file in the Tar archive
        with tarfile.open(export_path, "r:") as tf:
            tf_members = tf.getmembers()
            last_tf_member = tf_members[-1]
            assert last_tf_member.name == "exasol-manifest.json"
            assert last_tf_member.path == "exasol-manifest.json"
        images = find_images_by_tag(
            self.docker_client,
            lambda tag: tag.startswith(self.test_environment.docker_repository_name),
        )
        self.assertGreater(len(images), 0, "Images for repository were not found.")

    def test_docker_export_with_build_name(self):
        build_name = "TEST"
        export_result = api.export(
            flavor_path=(str(exaslct_utils.get_test_flavor()),),
            export_path=self.export_path,
            target_docker_repository_name=self.test_environment.docker_repository_name,
            build_name=build_name,
            compression_strategy=CompressionStrategy.NONE,
            force_rebuild=True,
        )
        export_info, export_path = export_test_utils.assert_single_release_export(
            self,
            export_result,
            self.export_path,
            flavor_path=str(exaslct_utils.get_test_flavor()),
            build_name=build_name,
        )
        self.assertEqual(export_path.suffix, ".tar")

        with tarfile.open(export_path, "r:") as tf:
            tf_members = tf.getmembers()
            last_tf_member = tf_members[-1]
            assert last_tf_member.name == "exasol-manifest.json"
            assert last_tf_member.path == "exasol-manifest.json"

        image_complete_name = export_info.depends_on_image.get_target_complete_name()
        self.assertIn(build_name, image_complete_name)
        self.assertNotIn(export_info.hash, image_complete_name)

        images = find_images_by_tag(
            self.docker_client,
            lambda tag: tag.startswith(self.test_environment.docker_repository_name),
        )
        self.assertGreater(len(images), 0, "Images for repository were not found.")


if __name__ == "__main__":
    unittest.main()
