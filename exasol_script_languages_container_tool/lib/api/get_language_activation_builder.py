import textwrap
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from attr import dataclass
from exasol_integration_test_docker_environment.lib.api.common import cli_function

from exasol_script_languages_container_tool.lib.tasks.upload.language_definition import (
    LanguageDefinition,
)


@dataclass
class LanguageDefinitionComponents:
    alias: str
    url: str

    def __str__(self) -> str:
        return f"{self.alias}={self.url}"

    @staticmethod
    def from_string(language_definition: str):
        lang_definition_separator = language_definition.find("=")
        if lang_definition_separator < 0:
            raise ValueError(f"Invalid language definition: '{language_definition}'")
        return LanguageDefinitionComponents(
            alias=language_definition[0:lang_definition_separator],
            url=language_definition[lang_definition_separator + 1 :],
        )


class LanguageDefinitionBuilder:
    def __init__(
        self,
        release_name: str,
        flavor_path: str,
        bucketfs_name: str,
        bucket_name: str,
        path_in_bucket: Optional[str],
        add_missing_builtin: bool = False,
    ):
        self.language_definition = LanguageDefinition(
            release_name=release_name,
            flavor_path=flavor_path,
            bucketfs_name=bucketfs_name,
            bucket_name=bucket_name,
            path_in_bucket=path_in_bucket,
            add_missing_builtin=add_missing_builtin,
        )
        self.custom_aliases: Dict[str, str] = dict()

    def add_custom_alias(self, orig_alias: str, custom_alias: str):
        self.custom_aliases[orig_alias] = custom_alias

    def generate_definition(self):
        lang_def_components_list = self.generate_definition_components()
        return " ".join(
            str(lang_def_components) for lang_def_components in lang_def_components_list
        )

    def _replace_alias(self, lang_def_components: LanguageDefinitionComponents):
        if (
            lang_def_components.alias in self.custom_aliases.keys()
            and not lang_def_components.url.startswith("builtin_")
        ):
            lang_def_components.alias = self.custom_aliases[lang_def_components.alias]
        return lang_def_components

    def generate_alter_session(self):
        return f"""ALTER SESSION SET SCRIPT_LANGUAGES='{self.generate_definition()}';"""

    def generate_alter_system(self):
        return f"""ALTER SYSTEM SET SCRIPT_LANGUAGES='{self.generate_definition()}';"""

    def generate_definition_components(self) -> List[LanguageDefinitionComponents]:
        language_definition = self.language_definition.generate_definition()
        return [
            self._replace_alias(LanguageDefinitionComponents.from_string(lang_def))
            for lang_def in language_definition.split(" ")
        ]


def get_language_activation_builder(
    flavor_path: str,
    bucketfs_name: str,
    bucket_name: str,
    container_name: str,
    path_in_bucket: str = "",
    add_missing_builtin: bool = False,
    custom_aliases: Optional[Dict[str, str]] = None,
) -> LanguageDefinitionBuilder:
    """
    Builds an object which can be used to build language activation statements, allowing custom aliases.
    :return: An instance of class LanguageDefinitionBuilder.
    """

    if custom_aliases is None:
        custom_aliases = dict()
    lang_def_builder = LanguageDefinitionBuilder(
        release_name=container_name,
        flavor_path=flavor_path,
        bucketfs_name=bucketfs_name,
        bucket_name=bucket_name,
        path_in_bucket=path_in_bucket,
        add_missing_builtin=add_missing_builtin,
    )
    if custom_aliases:
        for orig_alias, custom_alias in custom_aliases.items():
            lang_def_builder.add_custom_alias(orig_alias, custom_alias)
    return lang_def_builder
