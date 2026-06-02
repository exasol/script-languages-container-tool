import tempfile
from unittest.mock import patch

import pytest

from exasol.slc.tool.commands.generate_language_activation import (
    generate_language_activation,
)
from test.unit.cli import CliRunner


@pytest.fixture
def cli():
    return CliRunner(generate_language_activation)


def test_generate_language_activation_container_name(cli):
    with patch(
        "exasol.slc.api.generate_language_activation",
        return_value=("ALTER SESSION", "ALTER SYSTEM", "activation"),
    ) as mock_generate_language_activation:
        with tempfile.TemporaryDirectory() as temp_flavor_path:
            args = [
                "--flavor-path",
                temp_flavor_path,
                "--bucketfs-name",
                "bfsdefault",
                "--bucket-name",
                "default",
                "--path-in-bucket",
                "path",
                "--container-name",
                "container",
            ]
            cli.run(*args)

    assert cli.succeeded
    assert "activation" in cli.output
    mock_generate_language_activation.assert_called_once_with(
        temp_flavor_path,
        "bfsdefault",
        "default",
        "container",
        "path",
    )


@pytest.mark.parametrize("option_name", ["--build-name", "--release-name"])
def test_generate_language_activation_rejects_old_option_names(cli, option_name):
    with tempfile.TemporaryDirectory() as temp_flavor_path:
        args = [
            "--flavor-path",
            temp_flavor_path,
            "--bucketfs-name",
            "bfsdefault",
            "--bucket-name",
            "default",
            "--path-in-bucket",
            "path",
            option_name,
            "container",
        ]
        cli.run(*args)

    assert cli.failed
    assert "No such option" in cli.output
