import tempfile
import unittest
from pathlib import Path, PurePosixPath

import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.testing import utils  # type: ignore

from exasol_script_languages_container_tool.lib.api.get_language_activation_builder import (
    LanguageDefinitionComponents,
    get_language_activation_builder,
)
from exasol_script_languages_container_tool.lib.models.language_activation import (
    BuiltInLanguageDefinitionURL,
    ChrootPath,
    LanguageDefinitionURL,
    SLCLanguage,
    SLCParameter,
    UdfClientAbsolutePath,
)


class LanguageActivationBuilderTest(unittest.TestCase):
    flavor_path = str(exaslct_utils.get_real_test_flavor())

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.maxDiff = None

    def test_without_custom_alias_without_builtin(self):
        lang_act_build = get_language_activation_builder(
            flavor_path=self.flavor_path,
            bucketfs_name="bfsdefault",
            bucket_name="default",
            container_name="my_release",
            path_in_bucket="some_path",
        )
        components_list = lang_act_build.generate_definition_components()
        self.assertEqual(
            components_list,
            [
                LanguageDefinitionComponents(
                    alias="PYTHON3_TEST",
                    url=LanguageDefinitionURL(
                        protocol="localzmq+protobuf",
                        chroot_path=ChrootPath(
                            bucketfs_name="bfsdefault",
                            bucket_name="default",
                            path_in_bucket=PurePosixPath("some_path/my_release"),
                        ),
                        udf_client_path=UdfClientAbsolutePath(
                            bucketfs_name="bfsdefault",
                            bucket_name="default",
                            executable=PurePosixPath(
                                "some_path/my_release/exaudf/exaudfclient_py3"
                            ),
                        ),
                        parameters=[SLCParameter(key="lang", value=["python"])],
                    ),
                )
            ],
        )

    def test_without_custom_alias_with_builtin(self):
        lang_act_build = get_language_activation_builder(
            flavor_path=self.flavor_path,
            bucketfs_name="bfsdefault",
            bucket_name="default",
            container_name="my_release",
            path_in_bucket="some_path",
            add_missing_builtin=True,
        )
        components_list = lang_act_build.generate_definition_components()
        self.assertEqual(
            components_list,
            [
                LanguageDefinitionComponents(
                    alias="PYTHON3_TEST",
                    url=LanguageDefinitionURL(
                        protocol="localzmq+protobuf",
                        chroot_path=ChrootPath(
                            bucketfs_name="bfsdefault",
                            bucket_name="default",
                            path_in_bucket=PurePosixPath("some_path/my_release"),
                        ),
                        udf_client_path=UdfClientAbsolutePath(
                            bucketfs_name="bfsdefault",
                            bucket_name="default",
                            executable=PurePosixPath(
                                "some_path/my_release/exaudf/exaudfclient_py3"
                            ),
                        ),
                        parameters=[SLCParameter(key="lang", value=["python"])],
                    ),
                ),
                LanguageDefinitionComponents(
                    alias="JAVA",
                    url=BuiltInLanguageDefinitionURL(language=SLCLanguage.Java),
                ),
                LanguageDefinitionComponents(
                    alias="PYTHON3",
                    url=BuiltInLanguageDefinitionURL(language=SLCLanguage.Python3),
                ),
                LanguageDefinitionComponents(
                    alias="R",
                    url=BuiltInLanguageDefinitionURL(language=SLCLanguage.R),
                ),
            ],
        )

    def test_with_custom_alias_with_builtin(self):
        lang_act_build = get_language_activation_builder(
            flavor_path=self.flavor_path,
            bucketfs_name="bfsdefault",
            bucket_name="default",
            container_name="my_release",
            path_in_bucket="some_path",
            add_missing_builtin=True,
        )
        lang_act_build.add_custom_alias("PYTHON3_TEST", "MY_PYTHON3")
        lang_act_build.add_custom_alias("JAVA", "MY_JAVA")
        components_list = lang_act_build.generate_definition_components()
        self.assertEqual(
            components_list,
            [
                LanguageDefinitionComponents(
                    alias="MY_PYTHON3",
                    url=LanguageDefinitionURL(
                        protocol="localzmq+protobuf",
                        chroot_path=ChrootPath(
                            bucketfs_name="bfsdefault",
                            bucket_name="default",
                            path_in_bucket=PurePosixPath("some_path/my_release"),
                        ),
                        udf_client_path=UdfClientAbsolutePath(
                            bucketfs_name="bfsdefault",
                            bucket_name="default",
                            executable=PurePosixPath(
                                "some_path/my_release/exaudf/exaudfclient_py3"
                            ),
                        ),
                        parameters=[SLCParameter(key="lang", value=["python"])],
                    ),
                ),
                LanguageDefinitionComponents(
                    alias="JAVA",
                    url=BuiltInLanguageDefinitionURL(language=SLCLanguage.Java),
                ),
                LanguageDefinitionComponents(
                    alias="PYTHON3",
                    url=BuiltInLanguageDefinitionURL(language=SLCLanguage.Python3),
                ),
                LanguageDefinitionComponents(
                    alias="R",
                    url=BuiltInLanguageDefinitionURL(language=SLCLanguage.R),
                ),
            ],
        )

    def test_with_custom_alias_with_builtin_alter_session(self):
        lang_act_build = get_language_activation_builder(
            flavor_path=self.flavor_path,
            bucketfs_name="bfsdefault",
            bucket_name="default",
            container_name="my_release",
            path_in_bucket="some_path",
            add_missing_builtin=True,
        )
        lang_act_build.add_custom_alias("PYTHON3_TEST", "MY_PYTHON3")
        lang_act_build.add_custom_alias("JAVA", "MY_JAVA")
        alter_session = lang_act_build.generate_alter_session()
        self.assertEqual(
            alter_session,
            "ALTER SESSION SET SCRIPT_LANGUAGES='MY_PYTHON3="
            "localzmq+protobuf:///bfsdefault/default/some_path/my_release"
            "?lang=python#buckets/bfsdefault/default/some_path/my_release"
            "/exaudf/exaudfclient_py3 JAVA=builtin_java "
            "PYTHON3=builtin_python3 R=builtin_r';",
        )

    def test_with_custom_alias_with_builtin_alter_system(self):
        lang_act_build = get_language_activation_builder(
            flavor_path=self.flavor_path,
            bucketfs_name="bfsdefault",
            bucket_name="default",
            container_name="my_release",
            path_in_bucket="some_path",
            add_missing_builtin=True,
        )
        lang_act_build.add_custom_alias("PYTHON3_TEST", "MY_PYTHON3")
        lang_act_build.add_custom_alias("JAVA", "MY_JAVA")
        alter_session = lang_act_build.generate_alter_system()
        self.assertEqual(
            alter_session,
            "ALTER SYSTEM SET SCRIPT_LANGUAGES='MY_PYTHON3="
            "localzmq+protobuf:///bfsdefault/default/some_path/my_release"
            "?lang=python#buckets/bfsdefault/default/some_path/my_release"
            "/exaudf/exaudfclient_py3 JAVA=builtin_java "
            "PYTHON3=builtin_python3 R=builtin_r';",
        )

    def test_with_custom_alias_with_builtin_with_parameter_alter_system(self):
        with tempfile.TemporaryDirectory() as d:
            flavor_base_path = Path(d) / "flavor_base"
            flavor_base_path.mkdir()
            lang_def_file = flavor_base_path / "language_definition"
            with open(lang_def_file, "w") as f:
                f.write(
                    "PYTHON3_TEST=localzmq+protobuf:///{{ bucketfs_name }}/{{ bucket_name }}/{{ path_in_bucket }}"
                    "{{ release_name }}?lang=python&my_param=hello#buckets/{{ bucketfs_name }}/{{ bucket_name }}/"
                    "{{ path_in_bucket }}{{ release_name }}/exaudf/exaudfclient_py3"
                )
            lang_act_build = get_language_activation_builder(
                flavor_path=d,
                bucketfs_name="bfsdefault",
                bucket_name="default",
                container_name="my_release",
                path_in_bucket="some_path",
                add_missing_builtin=True,
            )
            lang_act_build.add_custom_alias("PYTHON3_TEST", "MY_PYTHON3")
            lang_act_build.add_custom_alias("JAVA", "MY_JAVA")
            alter_session = lang_act_build.generate_alter_system()
            self.assertEqual(
                alter_session,
                "ALTER SYSTEM SET SCRIPT_LANGUAGES='MY_PYTHON3="
                "localzmq+protobuf:///bfsdefault/default/some_path/my_release"
                "?lang=python&my_param=hello#buckets/bfsdefault/default/some_path/my_release"
                "/exaudf/exaudfclient_py3 JAVA=builtin_java "
                "PYTHON3=builtin_python3 R=builtin_r';",
            )


if __name__ == "__main__":
    unittest.main()
