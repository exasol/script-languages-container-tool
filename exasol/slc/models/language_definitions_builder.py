from typing import Dict, List

from exasol.slc.models.language_definition_components import (
    LanguageDefinitionComponents,
)


class LanguageDefinitionsBuilder:
    """
    Provides generation of "ALTER SESSION", "ALTER SYSTEM" commands and pure language definitions string
    replacing the aliases provides in the source Language Definition Components with custom aliases.
    """

    def __init__(self, lang_def_components: list[LanguageDefinitionComponents]) -> None:
        self.lang_def_components = lang_def_components
        self.custom_aliases: dict[str, str] = dict()

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

    def generate_definition_components(self) -> list[LanguageDefinitionComponents]:
        return [self._replace_alias(lang_def) for lang_def in self.lang_def_components]
