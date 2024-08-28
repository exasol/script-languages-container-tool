from pathlib import Path
from typing import Dict, List, Optional

from jinja2 import Template

from exasol_script_languages_container_tool.lib.api.language_activation import (
    BuiltInLanguageDefinitionURL,
    LanguageDefinitionComponents,
    LanguageDefinitionURL,
    SLCLanguage,
)
from exasol_script_languages_container_tool.lib.utils.language_def_parser import (
    parse_language_definition,
)


class LanguageDefinitionBuilder:
    def __init__(self, lang_def_components: List[LanguageDefinitionComponents]):
        self.lang_def_components = lang_def_components
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
            and not lang_def_components.is_builtin
        ):
            lang_def_components.alias = self.custom_aliases[lang_def_components.alias]
        return lang_def_components

    def generate_alter_session(self):
        return f"""ALTER SESSION SET SCRIPT_LANGUAGES='{self.generate_definition()}';"""

    def generate_alter_system(self):
        return f"""ALTER SYSTEM SET SCRIPT_LANGUAGES='{self.generate_definition()}';"""

    def generate_definition_components(self) -> List[LanguageDefinitionComponents]:
        return [self._replace_alias(lang_def) for lang_def in self.lang_def_components]


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
        bucketfs_name="", bucket_name="", release_name="", path_in_bucket=""
    )
    languages_defs = language_definition.split(" ")
    language_def_components_list = list()
    for lang_def in languages_defs:
        alias, url = parse_language_definition(lang_def)
        if type(url) is LanguageDefinitionURL:
            url.bucket_name = bucket_name
            url.bucketfs_name = bucketfs_name
            url.path_in_bucket = path_in_bucket
            url.container_name = container_name
        language_def_components_list.append(
            LanguageDefinitionComponents(alias=alias, url=url)
        )

    if add_missing_builtin:
        builtin_aliases = {slc_lang.name.upper(): slc_lang for slc_lang in SLCLanguage}
        defined_aliases = [
            lang_def_comp.alias.upper()
            for lang_def_comp in language_def_components_list
        ]
        missing_aliases = builtin_aliases.keys() - set(defined_aliases)
        for alias in sorted(list(missing_aliases)):
            built_in_lang_def_comp = LanguageDefinitionComponents(
                alias=alias,
                url=BuiltInLanguageDefinitionURL(language=builtin_aliases[alias]),
            )
            language_def_components_list.append(built_in_lang_def_comp)
    lang_def_builder = LanguageDefinitionBuilder(
        lang_def_components=language_def_components_list
    )

    if custom_aliases:
        for orig_alias, custom_alias in custom_aliases.items():
            lang_def_builder.add_custom_alias(orig_alias, custom_alias)
    return lang_def_builder
