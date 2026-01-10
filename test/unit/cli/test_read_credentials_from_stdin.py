import pytest
from unittest.mock import patch

from exasol.slc.tool.commands.deploy import read_credentials_from_stdin


def test_prompts_for_bucketfs_password_and_keeps_saas_token():
    with patch("getpass.getpass") as mocked_getpass:
        mocked_getpass.return_value = "bucket-pass-123"
        bucketfs_password, saas_token = read_credentials_from_stdin(
            bucketfs_name="my-bucket",
            bucketfs_password=None,
            bucketfs_user="deploy-user",
            saas_token="existing-saas-token",
            saas_account_id=None,
        )

        mocked_getpass.assert_called_once_with(
            "BucketFS Password for BucketFS {} and User {}:".format("my-bucket", "deploy-user")
        )
        assert bucketfs_password == "bucket-pass-123"
        assert saas_token == "existing-saas-token"


def test_prompts_for_saas_token_when_bucketfs_password_present():
    with patch("getpass.getpass") as mocked_getpass:
        mocked_getpass.return_value = "saas-token-xyz"
        bucketfs_password, saas_token = read_credentials_from_stdin(
            bucketfs_name="my-bucket",
            bucketfs_password="already-set",
            bucketfs_user="deploy-user",
            saas_token=None,
            saas_account_id="acct-42",
        )

        mocked_getpass.assert_called_once_with(
            "SaaS Token for Account {}:".format("acct-42")
        )
        assert bucketfs_password == "already-set"
        assert saas_token == "saas-token-xyz"


def test_no_prompt_when_both_credentials_present():
    # getpass.getpass must not be called in this case
    def fail_if_called(prompt):
        raise AssertionError("getpass.getpass should not be called")

    with patch("getpass.getpass", side_effect=fail_if_called):
        bucketfs_password, saas_token = read_credentials_from_stdin(
            bucketfs_name="my-bucket",
            bucketfs_password="present-pass",
            bucketfs_user="deploy-user",
            saas_token="present-saas",
            saas_account_id="acct-42",
        )

        assert bucketfs_password == "present-pass"
        assert saas_token == "present-saas"


def test_bucketfs_prompt_takes_precedence_over_saas_prompt():
    # If both bucketfs_password and saas_token are None, but bucketfs_name/user are present,
    # the function should prompt for the BucketFS password and return before prompting for SaaS token.
    with patch("getpass.getpass") as mocked_getpass:
        mocked_getpass.return_value = "only-bucket-pass"
        bucketfs_password, saas_token = read_credentials_from_stdin(
            bucketfs_name="my-bucket",
            bucketfs_password=None,
            bucketfs_user="deploy-user",
            saas_token=None,
            saas_account_id="acct-42",
        )

        mocked_getpass.assert_called_once_with(
            "BucketFS Password for BucketFS {} and User {}:".format("my-bucket", "deploy-user")
        )
        assert bucketfs_password == "only-bucket-pass"
        assert saas_token is None