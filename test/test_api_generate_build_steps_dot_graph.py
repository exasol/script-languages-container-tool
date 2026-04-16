import tempfile
import unittest
from pathlib import Path

import utils as exaslct_utils  # type: ignore # pylint: disable=import-error

from exasol.slc.api import generate_build_steps_dot_graph


class GenerateBuildStepsDotGraphTest(unittest.TestCase):

    def test_generate_dot_graph_matches_expected(self):
        flavor_path = exaslct_utils.get_test_flavor()
        expected_dot_file = (
            flavor_path / "flavor_base" / "test-flavor.dot"
        )
        expected_content = expected_dot_file.read_text(encoding="utf-8")
        result = generate_build_steps_dot_graph(
            flavor_path=str(flavor_path),
        )
        self.assertEqual(expected_content, result)

    def test_generate_dot_graph_writes_to_file(self):
        flavor_path = exaslct_utils.get_test_flavor()
        expected_dot_file = (
            flavor_path / "flavor_base" / "test-flavor.dot"
        )
        expected_content = expected_dot_file.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = str(Path(tmp_dir) / "output.dot")
            result = generate_build_steps_dot_graph(
                flavor_path=str(flavor_path),
                output_path=output_path,
            )
            written_content = Path(output_path).read_text(encoding="utf-8")
            self.assertEqual(expected_content, written_content)
            self.assertEqual(expected_content, result)


if __name__ == "__main__":
    unittest.main()
