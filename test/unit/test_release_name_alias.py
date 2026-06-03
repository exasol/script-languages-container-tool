from contextlib import ExitStack
from importlib import import_module
from unittest.mock import patch

import pytest


def _run_root_task(root_task_generator, **_kwargs):
    root_task_generator()
    return {}


def _assert_build_name_clears_stale_config(
    module_path: str,
    command_name: str,
    call_kwargs: dict[str, object],
) -> None:
    module = import_module(module_path)
    with ExitStack() as stack:
        stack.enter_context(patch.object(module, "import_build_steps"))
        set_build_config_mock = stack.enter_context(
            patch.object(module, "set_build_config")
        )
        stack.enter_context(
            patch.object(module, "generate_root_task", return_value=lambda: None)
        )
        stack.enter_context(
            patch.object(module, "run_task", side_effect=_run_root_task)
        )

        getattr(module, command_name)(**call_kwargs)

    assert set_build_config_mock.call_args.args[-1] == ""


def _assert_release_name_alias(
    module_path: str,
    command_name: str,
    *,
    build_name: str | None,
    release_name: str | None,
    expected_build_name: str | None,
) -> None:
    module = import_module(module_path)
    with ExitStack() as stack:
        stack.enter_context(patch.object(module, "import_build_steps"))
        set_build_config_mock = stack.enter_context(
            patch.object(module, "set_build_config")
        )
        generate_root_task_mock = stack.enter_context(
            patch.object(module, "generate_root_task")
        )
        stack.enter_context(
            patch.object(module, "run_task", side_effect=_run_root_task)
        )

        with pytest.warns(DeprecationWarning, match="release_name is deprecated"):
            getattr(module, command_name)(
                flavor_path=("flavor",),
                build_name=build_name,
                release_name=release_name,
            )

    assert set_build_config_mock.call_args.args[-1] == expected_build_name
    assert (
        generate_root_task_mock.call_args.kwargs["release_name"]
        == expected_build_name
    )


@pytest.mark.parametrize(
    "build_name, release_name, expected_build_name",
    [
        (None, "legacy-build", "legacy-build"),
        ("canonical-build", "legacy-build", "canonical-build"),
    ],
)
def test_export_release_name_alias(build_name, release_name, expected_build_name):
    _assert_release_name_alias(
        "exasol.slc.api.export",
        "export",
        build_name=build_name,
        release_name=release_name,
        expected_build_name=expected_build_name,
    )


@pytest.mark.parametrize(
    "build_name, release_name, expected_build_name",
    [
        (None, "legacy-build", "legacy-build"),
        ("canonical-build", "legacy-build", "canonical-build"),
    ],
)
def test_deploy_release_name_alias(build_name, release_name, expected_build_name):
    _assert_release_name_alias(
        "exasol.slc.api.deploy",
        "deploy",
        build_name=build_name,
        release_name=release_name,
        expected_build_name=expected_build_name,
    )


@pytest.mark.parametrize(
    "module_path, command_name, call_kwargs",
    [
        (
            "exasol.slc.api.build",
            "build",
            {"flavor_path": ("flavor",)},
        ),
        (
            "exasol.slc.api.upload",
            "upload",
            {
                "flavor_path": ("flavor",),
                "database_host": "localhost",
                "bucketfs_port": 1234,
                "bucketfs_username": "w",
                "bucketfs_name": "bfsdefault",
                "bucket_name": "default",
                "bucketfs_password": "secret",
            },
        ),
        (
            "exasol.slc.api.export",
            "export",
            {"flavor_path": ("flavor",)},
        ),
        (
            "exasol.slc.api.deploy",
            "deploy",
            {
                "flavor_path": ("flavor",),
                "bucketfs_host": "localhost",
                "bucketfs_port": 1234,
                "bucketfs_user": "w",
                "bucketfs_name": "bfsdefault",
                "bucket": "default",
                "bucketfs_password": "secret",
            },
        ),
    ],
)
def test_build_name_none_clears_stale_config(
    module_path: str,
    command_name: str,
    call_kwargs: dict[str, object],
):
    _assert_build_name_clears_stale_config(module_path, command_name, call_kwargs)
