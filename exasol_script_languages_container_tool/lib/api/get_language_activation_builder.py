from pathlib import Path
from typing import Dict, Optional

from jinja2 import Template

from exasol_script_languages_container_tool.lib.models.language_activation import (
    LanguageDefinitionComponents,
    LanguageDefinitionURL,
)
from exasol_script_languages_container_tool.lib.models.language_activation_builder import (
    LanguageDefinitionBuilder,
    add_missing_builtin_languages,
)
from exasol_script_languages_container_tool.lib.tasks.upload.language_def_parser import (
    parse_language_definition,
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
    with open(Path(flavor_path) / "flavor_base" / "language_definition") as f:
        lang_def_template = f.read()

    template = Template(lang_def_template)
    language_definition = template.render(
        bucketfs_name="",
        bucket_name="",
        release_name="",
        path_in_bucket="____end_marker_bucket_path____",
    )
    languages_defs = language_definition.split(" ")
    language_def_components_list = list()
    for lang_def in languages_defs:
        alias, url = parse_language_definition(
            lang_def, end_marker_bucket_path="____end_marker_bucket_path____"
        )
        if isinstance(url, LanguageDefinitionURL):
            url.chroot_bucket_name = bucket_name
            url.chroot_bucketfs_name = bucketfs_name
            url.chroot_path_in_bucket = f"{path_in_bucket}/{container_name}"
            url.udf_client_bucket_name = bucket_name
            url.udf_client_bucketfs_name = bucketfs_name
            url.udf_client_path_in_bucket = f"{path_in_bucket}/{container_name}"
        language_def_components_list.append(
            LanguageDefinitionComponents(alias=alias, url=url)
        )

    if add_missing_builtin:
        language_def_components_list = add_missing_builtin_languages(
            language_def_components_list
        )

    lang_def_builder = LanguageDefinitionBuilder(language_def_components_list)

    if custom_aliases:
        for orig_alias, custom_alias in custom_aliases.items():
            lang_def_builder.add_custom_alias(orig_alias, custom_alias)
    return lang_def_builder
