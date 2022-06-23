import unittest
from pathlib import Path
from typing import List, Callable

from exasol_integration_test_docker_environment.testing import exaslct_test_environment

EXASLCT_DEFAULT_BIN = Path(Path(__file__).parent.parent, "exaslct")


class ExaslctTestEnvironmentWithCleanUp(exaslct_test_environment.ExaslctTestEnvironment):

    def close(self):
        try:
            if self.clean_images_at_close:
                self.clean_all_images()
        except Exception as e:
            print(e)
        super().close()

    def clean_all_images(self):
        self.run_command(f"{self.executable} clean-all-images", use_flavor_path=False, clean=True)


def multiassert(assert_list: List[Callable], unit_test: unittest.TestCase):
    failure_log: List[str] = []
    for assert_fn in assert_list:
        try:
            assert_fn()
        except AssertionError as e:
            failure_log.append(f"\nFailure {len(failure_log)}: {str(e)}")

    if len(failure_log) != 0:
        res_failure_log = '\n'.join(failure_log)
        unit_test.fail(f"{len(failure_log)} failures within test.\n {res_failure_log}")
