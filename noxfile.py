import json
from argparse import ArgumentParser
from enum import Enum
from inspect import cleandoc

import nox

# imports all nox task provided by the toolbox
from exasol.toolbox.nox.tasks import *  # type: ignore

from clean_dockerhub import call_clean_dockerhub

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


@nox.session(name="cleanup-docker-hub", python=False)
def cleanup_docker_hub(session: nox.Session):
    """
    Removes docker hub tags older than `min_age_in_days` days.
    """
    parser = ArgumentParser(
        usage=f"nox -s {session.name} -- --docker-repository <repository> --docker-username <username> --docker-password <password> --min-age-days <min_age_in_days>"
    )
    parser.add_argument(
        "--docker-repository",
        type=str,
        required=True,
        help="Docker Repository name",
    )
    parser.add_argument(
        "--docker-username",
        type=str,
        required=True,
        help="Docker username",
    )
    parser.add_argument(
        "--docker-password",
        type=str,
        required=True,
        help="Docker password/PAT",
    )
    parser.add_argument(
        "--min-age-in-days",
        type=int,
        required=True,
        help="Minimum age in days of tags which will be removed",
    )
    parser.add_argument(
        "--max-number-pages",
        type=int,
        default=100,
        required=False,
        help=cleandoc(
            """Maximum number of pages.
        The page size is fixed at 100 (maximum from Dockerhub RestAPI).
        This means 100*MAX_NUMBER_PAGES will be deleted.
        Tags newer than MIN_AGE_IN_DAYS do not count.
        Use 0 for no maximum number (risk to take very long)"""
        ),
    )
    args = parser.parse_args(session.posargs)
    call_clean_dockerhub(
        docker_repository=args.docker_repository,
        docker_username=args.docker_username,
        docker_password=args.docker_password,
        min_age_in_days=args.min_age_in_days,
        max_number_of_pages=args.max_number_pages,
    )
