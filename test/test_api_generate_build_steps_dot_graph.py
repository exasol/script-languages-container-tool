import shutil
import tempfile
import unittest
from pathlib import Path

import utils as exaslct_utils  # type: ignore # pylint: disable=import-error

from exasol.slc.api import generate_build_steps_dot_graph

EXPECTED_DOT_FILE = (
    exaslct_utils.DEFAULT_FLAVOR_FLAVORS_ROOT_DIRECTORY
    / "test-flavor"
    / "build_steps.dot"
)


class GenerateBuildStepsDotGraphTest(unittest.TestCase):

    def test_generate_dot_graph_matches_expected(self):
        expected_content = EXPECTED_DOT_FILE.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp_dir:
            flavor_copy = Path(tmp_dir) / "test-flavor"
            shutil.copytree(exaslct_utils.get_test_flavor(), flavor_copy)
            result = generate_build_steps_dot_graph(
                flavor_path=str(flavor_copy),
            )
            default_output = flavor_copy / "build_steps.dot"
            self.assertTrue(default_output.exists())
            written_content = default_output.read_text(encoding="utf-8")
            self.assertEqual(expected_content, written_content)
            self.assertEqual(expected_content, result)

    def test_generate_dot_graph_writes_to_custom_path(self):
        expected_content = EXPECTED_DOT_FILE.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = str(Path(tmp_dir) / "custom.dot")
            result = generate_build_steps_dot_graph(
                flavor_path=str(exaslct_utils.get_test_flavor()),
                output_path=output_path,
            )
            written_content = Path(output_path).read_text(encoding="utf-8")
            self.assertEqual(expected_content, written_content)
            self.assertEqual(expected_content, result)


if __name__ == "__main__":
    unittest.main()
