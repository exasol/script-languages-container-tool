import tempfile
from test.unit.cli import CliRunner
from unittest.mock import patch

import exasol.bucketfs as bfs  # type: ignore
import pytest

from exasol.slc.models.deploy_result import DeployResult
from exasol.slc.models.language_definition_components import (
    BuiltInLanguageDefinitionURL,
    LanguageDefinitionComponents,
    SLCLanguage,
)
from exasol.slc.models.language_definitions_builder import LanguageDefinitionsBuilder
from exasol.slc.tool.commands.deploy import deploy


@pytest.fixture
def cli():
    return CliRunner(deploy)


def test_no_flavor_path(cli):
    assert cli.run().failed and "Missing option '--flavor-path'" in cli.output


TEST_BUCKETFS_HOST = "dummy-bucketfs-host"
TEST_BUCKETFS_PORT = 123
TEST_BUCKETFS_USER = "dummy-bucketfs-user"
TEST_BUCKETFS_PASSWORD = "dummy-bucketfs-password"
TEST_BUCKETFS_NAME = "dummy-bucketfs-name"
TEST_BUCKET_NAME = "dummy-bucket-name"

TEST_RELEASE_PATH = "/release_target"
TEST_UPLOAD_URL = "https://my_bucket/target"
TEST_LANG_DEF_BUILDER = LanguageDefinitionsBuilder(
    [
        LanguageDefinitionComponents(
            alias="dummy-alias", url=BuiltInLanguageDefinitionURL(SLCLanguage.Java)
        )
    ]
)
TEST_DUMMY_FLAVOR = "dummy-flavor"
TEST_DUMMY_RELEASE = "dummy-release"


def test_deploy_minimum_parameters(cli):
    return_value = {
        TEST_DUMMY_FLAVOR: {
            TEST_DUMMY_FLAVOR: DeployResult(
                release_path=TEST_RELEASE_PATH,
                human_readable_upload_location=TEST_UPLOAD_URL,
                bucket_path=None,
                language_definition_builder=TEST_LANG_DEF_BUILDER,
            )
        }
    }

    with patch(
        "exasol.slc.api.deploy",
        return_value=return_value,
    ) as mock_foo:
        with tempfile.TemporaryDirectory() as temp_flavor_path:
            cli.run(
                "--flavor-path",
                temp_flavor_path,
                "--bucketfs-host",
                TEST_BUCKETFS_HOST,
                "--bucketfs-port",
                TEST_BUCKETFS_PORT,
                "--bucketfs-user",
                TEST_BUCKETFS_USER,
                "--bucketfs-password",
                TEST_BUCKETFS_PASSWORD,
                "--bucketfs-name",
                TEST_BUCKETFS_NAME,
                "--bucket",
                TEST_BUCKET_NAME,
            )
        assert (
            cli.succeeded
            and "Uploaded release='dummy-flavor' located at /release_target to https://my_bucket/target"
            in cli.output
        )
        mock_foo.assert_called_once_with(
            flavor_path=(temp_flavor_path,),
            bucketfs_host=TEST_BUCKETFS_HOST,
            bucketfs_port=TEST_BUCKETFS_PORT,
            bucketfs_user=TEST_BUCKETFS_USER,
            bucketfs_name=TEST_BUCKETFS_NAME,
            bucket=TEST_BUCKET_NAME,
            bucketfs_password=TEST_BUCKETFS_PASSWORD,
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


def test_deploy_password_in_env(cli):
    return_value = {
        TEST_DUMMY_FLAVOR: {
            TEST_DUMMY_FLAVOR: DeployResult(
                release_path=TEST_RELEASE_PATH,
                human_readable_upload_location=TEST_UPLOAD_URL,
                bucket_path=None,
                language_definition_builder=TEST_LANG_DEF_BUILDER,
            )
        }
    }

    TEST_ENV_PASSWORD = "super_secret_bucketfs_password"

    cli.env = {"BUCKETFS_PASSWORD": TEST_ENV_PASSWORD}
    with patch(
        "exasol.slc.api.deploy",
        return_value=return_value,
    ) as mock_foo:
        with tempfile.TemporaryDirectory() as temp_flavor_path:
            cli.run(
                "--flavor-path",
                temp_flavor_path,
                "--bucketfs-host",
                TEST_BUCKETFS_HOST,
                "--bucketfs-port",
                TEST_BUCKETFS_PORT,
                "--bucketfs-user",
                TEST_BUCKETFS_USER,
                "--bucketfs-name",
                TEST_BUCKETFS_NAME,
                "--bucket",
                TEST_BUCKET_NAME,
            )
        assert (
            cli.succeeded
            and "Uploaded release='dummy-flavor' located at /release_target to https://my_bucket/target"
            in cli.output
        )
        mock_foo.assert_called_once_with(
            flavor_path=(temp_flavor_path,),
            bucketfs_host=TEST_BUCKETFS_HOST,
            bucketfs_port=TEST_BUCKETFS_PORT,
            bucketfs_user=TEST_BUCKETFS_USER,
            bucketfs_name=TEST_BUCKETFS_NAME,
            bucket=TEST_BUCKET_NAME,
            bucketfs_password=TEST_ENV_PASSWORD,
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
