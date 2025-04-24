import json

import nox

# imports all nox task provided by the toolbox
from exasol.toolbox.nox.tasks import *  # type: ignore

# default actions to be run if nothing is explicitly specified with the -s option
nox.options.sessions = ["project:fix"]

from noxconfig import PROJECT_CONFIG


@nox.session(name="integration-test-list", python=False)
def run_integration_test_list(session: nox.Session):
    """
    Returns the test files under directory test (without walking subdirectories) as JSON list.
    """
    test_path = PROJECT_CONFIG.root / "test"
    tests = [{"path": str(t), "name": t.stem} for t in test_path.glob("test_*.py")]
    print(json.dumps(tests))
