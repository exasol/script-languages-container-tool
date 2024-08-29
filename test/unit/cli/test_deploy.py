import tempfile
from test.unit.cli import CliRunner
from unittest.mock import MagicMock, patch

import pytest

from exasol_script_languages_container_tool.cli.commands.deploy import deploy


class DummyLocalTarget:
    def __init__(self):
        self.mock = MagicMock()
        self.mock.read.return_value = "deploy was successful"

    def __enter__(self):
        return self.mock

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def cli():
    """
    To prevent accidentally creating actual AWS resources, the fixture
    tells the CliRunner to use an invalid AWS profile.
    """
    return CliRunner(deploy)


def test_no_flavor_path(cli):
    assert cli.run().failed and "Missing option '--flavor-path'" in cli.output


def test_deploy_minimum_parameters(cli):
    return_mock = MagicMock()
    dummy_returned_target = DummyLocalTarget()
    return_mock.open.return_value = dummy_returned_target

    with patch(
        "exasol_script_languages_container_tool.lib.api.deploy",
        return_value=return_mock,
    ) as mock_foo:
        with tempfile.TemporaryDirectory() as temp_flavor_path:
            cli.run(
                "--flavor-path",
                temp_flavor_path,
                "--bucketfs-host",
                "dummy-bucketfs-host",
                "--bucketfs-port",
                123,
                "--bucketfs-user",
                "dummy-bucketfs-user",
                "--bucketfs-password",
                "dummy-bucketfs-password",
                "--bucketfs-name",
                "dummy-bucketfs-name",
                "--bucket",
                "dummy-bucket-name",
            )
        assert cli.succeeded and "deploy was successful" in cli.output
        mock_foo.assert_called_once_with(
            flavor_path=(temp_flavor_path,),
            bucketfs_host="dummy-bucketfs-host",
            bucketfs_port=123,
            bucketfs_user="dummy-bucketfs-user",
            bucketfs_name="dummy-bucketfs-name",
            bucket="dummy-bucket-name",
            bucketfs_password="dummy-bucketfs-password",
            bucketfs_use_https=False,
            path_in_bucket="",
            release_goal=("release",),
            release_name=None,
            force_rebuild=False,
            force_rebuild_from=(),
            force_pull=False,
            output_directory=".build_output",
            temporary_base_directory="/tmp",
            log_build_context_content=False,
            cache_directory=None,
            build_name=None,
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
            ssl_cert_path="",
            use_ssl_cert_validation=True,
        )
    return_mock.open.assert_called_once()
    dummy_returned_target.mock.read.assert_called_once()


def test_deploy_password_in_env(cli):
    return_mock = MagicMock()
    dummy_returned_target = DummyLocalTarget()
    return_mock.open.return_value = dummy_returned_target

    cli.env = {"BUCKETFS_PASSWORD": "super_secret_bucketfs_password"}
    with patch(
        "exasol_script_languages_container_tool.lib.api.deploy",
        return_value=return_mock,
    ) as mock_foo:
        with tempfile.TemporaryDirectory() as temp_flavor_path:
            cli.run(
                "--flavor-path",
                temp_flavor_path,
                "--bucketfs-host",
                "dummy-bucketfs-host",
                "--bucketfs-port",
                123,
                "--bucketfs-user",
                "dummy-bucketfs-user",
                "--bucketfs-name",
                "dummy-bucketfs-name",
                "--bucket",
                "dummy-bucket-name",
            )
        assert cli.succeeded and "deploy was successful" in cli.output
    mock_foo.assert_called_once_with(
        flavor_path=(temp_flavor_path,),
        bucketfs_host="dummy-bucketfs-host",
        bucketfs_port=123,
        bucketfs_user="dummy-bucketfs-user",
        bucketfs_name="dummy-bucketfs-name",
        bucket="dummy-bucket-name",
        bucketfs_password="super_secret_bucketfs_password",
        bucketfs_use_https=False,
        path_in_bucket="",
        release_goal=("release",),
        release_name=None,
        force_rebuild=False,
        force_rebuild_from=(),
        force_pull=False,
        output_directory=".build_output",
        temporary_base_directory="/tmp",
        log_build_context_content=False,
        cache_directory=None,
        build_name=None,
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
        ssl_cert_path="",
        use_ssl_cert_validation=True,
    )
    return_mock.open.assert_called_once()
    dummy_returned_target.mock.read.assert_called_once()
