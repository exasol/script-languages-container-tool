import tempfile
from test.unit.cli import CliRunner
from unittest.mock import patch

import pytest

from exasol.slc.tool.commands.build import build


@pytest.fixture
def cli():
    return CliRunner(build)


def test_build_name(cli):
    with patch("exasol.slc.api.build", return_value={}) as mock_build:
        with tempfile.TemporaryDirectory() as temp_flavor_path:
            cli.run(
                "--flavor-path",
                temp_flavor_path,
                "--build-name",
                "canonical-build",
            )

    assert cli.succeeded
    mock_build.assert_called_once_with(
        flavor_path=(temp_flavor_path,),
        goal=(),
        force_rebuild=False,
        force_rebuild_from=(),
        force_pull=False,
        output_directory=".build_output",
        temporary_base_directory="/var/tmp",
        log_build_context_content=False,
        cache_directory=None,
        build_name="canonical-build",
        shortcut_build=True,
        source_docker_repository_name="exasol/script-language-container",
        source_docker_tag_prefix="",
        source_docker_username=None,
        source_docker_password=None,
        target_docker_repository_name="exasol/script-language-container",
        target_docker_tag_prefix="",
        target_docker_username=None,
        target_docker_password=None,
        workers=5,
        task_dependencies_dot_file=None,
        log_level=None,
        use_job_specific_log_file=True,
    )
