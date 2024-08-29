from typing import Dict, List

from exasol_script_languages_container_tool.lib.models.language_activation import (
    BuiltInLanguageDefinitionURL,
    LanguageDefinitionComponents,
    SLCLanguage,
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


def add_missing_builtin_languages(
    language_def_components_list: List[LanguageDefinitionComponents],
) -> List[LanguageDefinitionComponents]:
    builtin_aliases = {slc_lang.name.upper(): slc_lang for slc_lang in SLCLanguage}
    defined_aliases = [
        lang_def_comp.alias.upper() for lang_def_comp in language_def_components_list
    ]
    missing_aliases = builtin_aliases.keys() - set(defined_aliases)
    for alias in sorted(list(missing_aliases)):
        built_in_lang_def_comp = LanguageDefinitionComponents(
            alias=alias,
            url=BuiltInLanguageDefinitionURL(language=builtin_aliases[alias]),
        )
        language_def_components_list.append(built_in_lang_def_comp)
    return language_def_components_list
