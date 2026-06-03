from contextlib import ExitStack
from importlib import import_module
from unittest.mock import patch

import pytest


def _run_root_task(root_task_generator, **_kwargs):
    root_task_generator()
    return {}


@pytest.mark.parametrize(
    "build_name, release_name, expected_build_name",
    [
        (None, "legacy-build", "legacy-build"),
        ("canonical-build", "legacy-build", "canonical-build"),
    ],
)
def test_export_release_name_alias(build_name, release_name, expected_build_name):
    module = import_module("exasol.slc.api.export")
    with ExitStack() as stack:
        stack.enter_context(patch.object(module, "import_build_steps"))
        set_build_config_mock = stack.enter_context(
            patch.object(module, "set_build_config")
        )
        generate_root_task_mock = stack.enter_context(
            patch.object(module, "generate_root_task")
        )
        stack.enter_context(patch.object(module, "run_task", side_effect=_run_root_task))

        with pytest.warns(DeprecationWarning, match="release_name is deprecated"):
            module.export(
                flavor_path=("flavor",),
                build_name=build_name,
                release_name=release_name,
            )

    assert set_build_config_mock.call_args.args[-1] == expected_build_name
    assert generate_root_task_mock.call_args.kwargs["release_name"] == expected_build_name


@pytest.mark.parametrize(
    "build_name, release_name, expected_build_name",
    [
        (None, "legacy-build", "legacy-build"),
        ("canonical-build", "legacy-build", "canonical-build"),
    ],
)
def test_deploy_release_name_alias(build_name, release_name, expected_build_name):
    module = import_module("exasol.slc.api.deploy")
    with ExitStack() as stack:
        stack.enter_context(patch.object(module, "import_build_steps"))
        set_build_config_mock = stack.enter_context(
            patch.object(module, "set_build_config")
        )
        generate_root_task_mock = stack.enter_context(
            patch.object(module, "generate_root_task")
        )
        stack.enter_context(patch.object(module, "run_task", side_effect=_run_root_task))

        with pytest.warns(DeprecationWarning, match="release_name is deprecated"):
            module.deploy(
                flavor_path=("flavor",),
                release_name=release_name,
                build_name=build_name,
            )

    assert set_build_config_mock.call_args.args[-1] == expected_build_name
    assert generate_root_task_mock.call_args.kwargs["release_name"] == expected_build_name


@pytest.mark.parametrize(
    "build_name, release_name, expected_build_name",
    [
        (None, "legacy-build", "legacy-build"),
        ("canonical-build", "legacy-build", "canonical-build"),
    ],
)
def test_upload_release_name_alias(build_name, release_name, expected_build_name):
    module = import_module("exasol.slc.api.upload")
    with ExitStack() as stack:
        stack.enter_context(patch.object(module, "import_build_steps"))
        set_build_config_mock = stack.enter_context(
            patch.object(module, "set_build_config")
        )
        generate_root_task_mock = stack.enter_context(
            patch.object(module, "generate_root_task")
        )
        stack.enter_context(patch.object(module, "run_task", side_effect=_run_root_task))

        with pytest.warns(DeprecationWarning, match="release_name is deprecated"):
            module.upload(
                flavor_path=("flavor",),
                database_host="db-host",
                bucketfs_port=123,
                bucketfs_username="w",
                bucketfs_name="bfs",
                bucket_name="bucket",
                bucketfs_password="password",
                build_name=build_name,
                release_name=release_name,
            )

    assert set_build_config_mock.call_args.args[-1] == expected_build_name
    assert generate_root_task_mock.call_args.kwargs["release_name"] == expected_build_name
