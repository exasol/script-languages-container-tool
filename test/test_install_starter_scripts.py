import tempfile
import unittest

import filecmp
from pathlib import Path

import pkg_resources

from exasol_script_languages_container_tool.lib.tasks.install_starter_scripts.run_starter_script_installation import \
    run_starter_script_installation

PACKAGE_IDENTITY = "exasol-script-languages-container-tool"
MODULE_IDENTITY = PACKAGE_IDENTITY.replace("-", "_")
TARGET_EXASLCT_SCRIPTS_DIR = "exaslct_scripts"


class InstallStarterScriptTests(unittest.TestCase):

    def test_positive(self):
        with tempfile.TemporaryDirectory() as target_dir:
            target_path = Path(target_dir)
            run_starter_script_installation(target_path, target_path / TARGET_EXASLCT_SCRIPTS_DIR)

            self.assertTrue(pkg_resources.resource_isdir(MODULE_IDENTITY, "starter_scripts"))
            source_exaslct_scripts_dir = pkg_resources.resource_filename(MODULE_IDENTITY, "starter_scripts")
            cmp_res = filecmp.dircmp(source_exaslct_scripts_dir, target_path / TARGET_EXASLCT_SCRIPTS_DIR)
            self.assertTrue(len(cmp_res.common) > 0)
            self.assertEqual(len(cmp_res.left_only), 0)
            self.assertEqual(len(cmp_res.right_only), 1)
            self.assertEqual(cmp_res.right_only[0], "exaslct.sh")
            exaslct_link = target_path / "exaslct"
            self.assertTrue(exaslct_link.exists() and exaslct_link.is_symlink())


if __name__ == '__main__':
    unittest.main()
