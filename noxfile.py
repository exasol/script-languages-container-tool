import json
from argparse import ArgumentParser
from enum import Enum

import nox

# imports all nox task provided by the toolbox
from exasol.toolbox.nox.tasks import *  # type: ignore

# default actions to be run if nothing is explicitly specified with the -s option
nox.options.sessions = ["project:fix"]

from noxconfig import PROJECT_CONFIG


class TestSet(Enum):
    GPU_ONLY = "gpu-only"
    DEFAULT = "default"


@nox.session(name="integration-test-list", python=False)
def run_integration_test_list(session: nox.Session):
    """
    Returns the test files under directory test (without walking subdirectories) as JSON list.
    """
    test_set_values = [ts.value for ts in TestSet]
    parser = ArgumentParser(
        usage=f"nox -s {session.name} -- --test-set {{{','.join(test_set_values)}}}"
    )
    parser.add_argument(
        "--test-set",
        type=TestSet,
        required=True,
        help="Test set name",
    )
    args = parser.parse_args(session.posargs)
    test_path = PROJECT_CONFIG.root / "test"
    if args.test_set == TestSet.GPU_ONLY:
        tests = [
            {"path": str(t), "name": t.stem}
            for t in test_path.glob("test_*.py")
            if "gpu" in t.name
        ]
    else:
        tests = [
            {"path": str(t), "name": t.stem}
            for t in test_path.glob("test_*.py")
            if "gpu" not in t.name
        ]
    print(json.dumps(tests))
