import tarfile
import unittest
from pathlib import Path

import docker
import export_test_utils  # type: ignore[import-not-found]
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

    def _run_export(self, build_name: str | None = None, **kwargs):
        export_result = api.export(
            flavor_path=(str(exaslct_utils.get_test_flavor()),),
            export_path=self.export_path,
            target_docker_repository_name=self.test_environment.docker_repository_name,
            force_rebuild=True,
            build_name=build_name,
            **kwargs,
        )
        return export_test_utils.assert_single_release_export(
            self,
            export_result,
            self.export_path,
            flavor_path=str(exaslct_utils.get_test_flavor()),
            build_name=build_name,
        )

    def _assert_manifest_is_last(self, export_path: Path) -> None:
        with tarfile.open(export_path, "r:*") as tf:
            last_tf_member = tf.getmembers()[-1]
            self.assertEqual(last_tf_member.name, "exasol-manifest.json")
            self.assertEqual(last_tf_member.path, "exasol-manifest.json")

    def _assert_repository_images(
        self, expected_count: int, *, exact: bool = False
    ) -> None:
        images = find_images_by_tag(
            self.docker_client,
            lambda tag: tag.startswith(self.test_environment.docker_repository_name),
        )
        if exact:
            self.assertEqual(
                len(images),
                expected_count,
                "Images for repository were not deleted.",
            )
        else:
            self.assertGreater(
                len(images),
                expected_count,
                "Images for repository were not found.",
            )

    def test_docker_export(self):
        export_info, export_path = self._run_export()
        self._assert_manifest_is_last(export_path)
        image_complete_name = export_info.depends_on_image.get_target_complete_name()
        self.assertIn(export_info.hash, image_complete_name)
        self._assert_repository_images(0)

    def test_docker_export_with_image_cleanup(self):
        export_info, export_path = self._run_export(cleanup_docker_images=True)
        self._assert_manifest_is_last(export_path)
        image_complete_name = export_info.depends_on_image.get_target_complete_name()
        self.assertIn(export_info.hash, image_complete_name)
        self._assert_repository_images(0, exact=True)

    def test_docker_export_uncompressed(self):
        export_info, export_path = self._run_export(
            compression_strategy=CompressionStrategy.NONE
        )
        self.assertEqual(export_path.suffix, ".tar")
        self._assert_manifest_is_last(export_path)
        image_complete_name = export_info.depends_on_image.get_target_complete_name()
        self.assertIn(export_info.hash, image_complete_name)
        self._assert_repository_images(0)

    def test_docker_export_with_build_name(self):
        build_name = "TEST"
        export_info, export_path = self._run_export(
            build_name=build_name,
            compression_strategy=CompressionStrategy.NONE,
        )
        self.assertEqual(export_path.suffix, ".tar")
        self._assert_manifest_is_last(export_path)
        image_complete_name = export_info.depends_on_image.get_target_complete_name()
        self.assertIn(build_name, image_complete_name)
        self.assertNotIn(export_info.hash, image_complete_name)
        self._assert_repository_images(0)

    def test_docker_export_with_symlink_for_export_path(self):
        export_info, export_path = self._run_export(
            use_symlink_for_export_path=True,
        )
        self.assertTrue(export_path.is_symlink())
        self.assertEqual(export_path.resolve(), Path(export_info.cache_file).resolve())
        self._assert_manifest_is_last(export_path)
        image_complete_name = export_info.depends_on_image.get_target_complete_name()
        self.assertIn(export_info.hash, image_complete_name)
        self._assert_repository_images(0)


if __name__ == "__main__":
    unittest.main()
