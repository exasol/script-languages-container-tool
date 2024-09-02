import os
import tarfile
import unittest
from pathlib import Path

import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.testing import utils  # type: ignore

from exasol.slc import api


class ApiDockerExportTest(unittest.TestCase):
    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctApiTestEnvironmentWithCleanup(
            self, True
        )
        self.export_path = self.test_environment.temp_dir + "/export_dir"
        self.test_environment.clean_all_images()

    def tearDown(self):
        utils.close_environments(self.test_environment)

    def test_docker_export(self):
        export_result = api.export(
            flavor_path=(str(exaslct_utils.get_test_flavor()),),
            export_path=self.export_path,
        )
        self.assertEqual(len(export_result.export_infos), 1)
        export_infos_for_flavor = export_result.export_infos[
            str(exaslct_utils.get_test_flavor())
        ]
        self.assertEqual(len(export_infos_for_flavor), 1)
        export_info = export_infos_for_flavor["release"]
        exported_files = os.listdir(self.export_path)
        export_path = Path(export_info.output_file)
        self.assertIn(export_path.name, exported_files)

        # Verify that "exasol-manifest.json" is the last file in the Tar archive
        with tarfile.open(export_path, "r:*") as tf:
            tf_members = tf.getmembers()
            last_tf_member = tf_members[-1]
            assert last_tf_member.name == "exasol-manifest.json"
            assert last_tf_member.path == "exasol-manifest.json"


if __name__ == "__main__":
    unittest.main()
