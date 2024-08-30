from typing import Dict, Optional

from exasol_script_languages_container_tool.lib.models.language_activation import (
    LanguageDefinitionComponents,
)
from exasol_script_languages_container_tool.lib.models.language_activation_builder import (
    LanguageDefinitionBuilder,
)
from exasol_script_languages_container_tool.lib.tasks.upload.language_def_parser import (
    parse_language_definition,
)
from exasol_script_languages_container_tool.lib.tasks.upload.language_definition import (
    LanguageDefinition,
)


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

    language_definition = LanguageDefinition(
        release_name=container_name,
        flavor_path=flavor_path,
        bucketfs_name=bucketfs_name,
        bucket_name=bucket_name,
        path_in_bucket=path_in_bucket,
        add_missing_builtin=add_missing_builtin,
    )
    language_definitions = language_definition.generate_definition().split(" ")
    language_def_components_list = list()
    for lang_def in language_definitions:
        alias, url = parse_language_definition(lang_def)
        language_def_components_list.append(
            LanguageDefinitionComponents(alias=alias, url=url)
        )

    lang_def_builder = LanguageDefinitionBuilder(language_def_components_list)

    if custom_aliases:
        for orig_alias, custom_alias in custom_aliases.items():
            lang_def_builder.add_custom_alias(orig_alias, custom_alias)
    return lang_def_builder
