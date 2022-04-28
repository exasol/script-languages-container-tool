import subprocess
import unittest
from pathlib import Path


class DockerBuildDirectTest(unittest.TestCase):

    def _execute_in_new_process(self, target):
        path = Path(__file__)
        args = ("python", f"{path.parent.absolute()}/docker_build_direct_subprocess.py", target)
        p = subprocess.run(args)
        p.check_returncode()

    def test_docker_build(self):
        self._execute_in_new_process("run_test_docker_build")


if __name__ == '__main__':
    unittest.main()
