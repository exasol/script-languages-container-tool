import os
import unittest
from pathlib import Path

import utils as exaslct_utils
from exasol_integration_test_docker_environment.testing import utils

from exasol_script_languages_container_tool.lib import api


class ApiDockerExportTest(unittest.TestCase):
    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctApiTestEnvironmentWithCleanup(self, True)
        self.export_path = self.test_environment.temp_dir + "/export_dir"
        self.test_environment.clean_all_images()

    def tearDown(self):
        utils.close_environments(self.test_environment)

    def test_docker_export(self):
        export_result = api.export(flavor_path=(str(self.test_environment.get_test_flavor()),),
                                   export_path=self.export_path)
        self.assertEqual(len(export_result.export_infos), 1)
        export_infos_for_flavor = export_result.export_infos[str(self.test_environment.get_test_flavor())]
        self.assertEqual(len(export_infos_for_flavor), 1)
        export_info = export_infos_for_flavor["release"]
        exported_files = os.listdir(self.export_path)
        export_path = Path(export_info.output_file)
        self.assertIn(export_path.name, exported_files)


if __name__ == '__main__':
    unittest.main()
