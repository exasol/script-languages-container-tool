import unittest
from test.utils import get_real_test_flavor

from exasol_script_languages_container_tool.lib.tasks.upload.language_definition import (
    LanguageDefinition,
)


class LanguageDefintionTest(unittest.TestCase):
    flavor_path = str(get_real_test_flavor())

    def test_add_missing_builtin_true(self):
        language_definition = LanguageDefinition(
            release_name="release_name",
            flavor_path=self.flavor_path,
            bucketfs_name="bucketfs_name",
            bucket_name="bucket_name",
            path_in_bucket="path_in_bucket",
            add_missing_builtin=True,
        )
        self.assertEqual(
            "PYTHON3_TEST=localzmq+protobuf:///bucketfs_name/bucket_name/path_in_bucket/release_name?lang=python#buckets/bucketfs_name/bucket_name/path_in_bucket/release_name/exaudf/exaudfclient_py3 JAVA=builtin_java PYTHON=builtin_python PYTHON3=builtin_python3 R=builtin_r",
            language_definition.generate_definition(),
        )

    def test_add_missing_builtin_false(self):
        language_definition = LanguageDefinition(
            release_name="release_name",
            flavor_path=self.flavor_path,
            bucketfs_name="bucketfs_name",
            bucket_name="bucket_name",
            path_in_bucket="path_in_bucket",
            add_missing_builtin=False,
        )
        self.assertEqual(
            "PYTHON3_TEST=localzmq+protobuf:///bucketfs_name/bucket_name/path_in_bucket/release_name?lang=python#buckets/bucketfs_name/bucket_name/path_in_bucket/release_name/exaudf/exaudfclient_py3",
            language_definition.generate_definition(),
        )

    def test_path_in_bucket_none(self):
        language_definition = LanguageDefinition(
            release_name="release_name",
            flavor_path=self.flavor_path,
            bucketfs_name="bucketfs_name",
            bucket_name="bucket_name",
            path_in_bucket=None,
        )
        self.assertEqual(
            "PYTHON3_TEST=localzmq+protobuf:///bucketfs_name/bucket_name/release_name?lang=python#buckets/bucketfs_name/bucket_name/release_name/exaudf/exaudfclient_py3",
            language_definition.generate_definition(),
        )

    def test_path_in_bucket_empyt_string(self):
        language_definition = LanguageDefinition(
            release_name="release_name",
            flavor_path=self.flavor_path,
            bucketfs_name="bucketfs_name",
            bucket_name="bucket_name",
            path_in_bucket="",
        )
        self.assertEqual(
            "PYTHON3_TEST=localzmq+protobuf:///bucketfs_name/bucket_name/release_name?lang=python#buckets/bucketfs_name/bucket_name/release_name/exaudf/exaudfclient_py3",
            language_definition.generate_definition(),
        )

    def test_path_in_bucket_not_none(self):
        language_definition = LanguageDefinition(
            release_name="release_name",
            flavor_path=self.flavor_path,
            bucketfs_name="bucketfs_name",
            bucket_name="bucket_name",
            path_in_bucket="path_in_bucket",
        )
        self.assertEqual(
            "PYTHON3_TEST=localzmq+protobuf:///bucketfs_name/bucket_name/path_in_bucket/release_name?lang=python#buckets/bucketfs_name/bucket_name/path_in_bucket/release_name/exaudf/exaudfclient_py3",
            language_definition.generate_definition(),
        )

    def test_alter_system(self):
        language_definition = LanguageDefinition(
            release_name="release_name",
            flavor_path=self.flavor_path,
            bucketfs_name="bucketfs_name",
            bucket_name="bucket_name",
            path_in_bucket="path_in_bucket",
        )
        self.assertEqual(
            "ALTER SYSTEM SET SCRIPT_LANGUAGES='PYTHON3_TEST=localzmq+protobuf:///bucketfs_name/bucket_name/path_in_bucket/release_name?lang=python#buckets/bucketfs_name/bucket_name/path_in_bucket/release_name/exaudf/exaudfclient_py3';",
            language_definition.generate_alter_system(),
        )

    def test_alter_session(self):
        language_definition = LanguageDefinition(
            release_name="release_name",
            flavor_path=self.flavor_path,
            bucketfs_name="bucketfs_name",
            bucket_name="bucket_name",
            path_in_bucket="path_in_bucket",
        )
        self.assertEqual(
            "ALTER SESSION SET SCRIPT_LANGUAGES='PYTHON3_TEST=localzmq+protobuf:///bucketfs_name/bucket_name/path_in_bucket/release_name?lang=python#buckets/bucketfs_name/bucket_name/path_in_bucket/release_name/exaudf/exaudfclient_py3';",
            language_definition.generate_alter_session(),
        )


if __name__ == "__main__":
    unittest.main()
