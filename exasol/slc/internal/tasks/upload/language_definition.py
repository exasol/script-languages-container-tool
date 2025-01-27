from pathlib import Path
from typing import Optional

from jinja2 import Template


class LanguageDefinition:
    def __init__(
        self,
        release_name: str,
        flavor_path: str,
        bucketfs_name: str,
        bucket_name: str,
        path_in_bucket: Optional[str],
        add_missing_builtin: bool = False,
    ) -> None:
        self.path_in_bucket = path_in_bucket
        self.bucket_name = bucket_name
        self.bucketfs_name = bucketfs_name
        self.flavor_path = flavor_path
        self.release_name = release_name
        self.add_missing_builtin = add_missing_builtin

    def generate_definition(self) -> str:
        language_definition = self._render_language_definition()
        if self.add_missing_builtin:
            language_definition = self._add_missing_builtin_language_definitions(
                language_definition
            )
        return language_definition.strip()

    def _render_language_definition(self) -> str:
        path_in_bucket = self.path_in_bucket if self.path_in_bucket is not None else ""
        if path_in_bucket != "" and not path_in_bucket.endswith("/"):
            path_in_bucket = path_in_bucket + "/"
        language_definition_path = Path(
            self.flavor_path, "flavor_base", "language_definition"
        )
        with language_definition_path.open("r") as f:
            language_definition_template = f.read()
        template = Template(language_definition_template)
        language_definition = template.render(
            bucketfs_name=self.bucketfs_name,
            bucket_name=self.bucket_name,
            path_in_bucket=path_in_bucket,
            release_name=self.release_name,
        )
        return language_definition

    def _add_missing_builtin_language_definitions(self, language_definition) -> str:
        builtin_aliases = {"PYTHON3", "JAVA", "R"}
        defined_aliases = {
            alias.split("=")[0] for alias in language_definition.split(" ")
        }
        missing_aliases = builtin_aliases - defined_aliases
        sorted_missing_aliases = sorted(missing_aliases)
        additional_language_defintions = " ".join(
            f"{alias}=builtin_{alias.lower()}" for alias in sorted_missing_aliases
        )
        language_definition = f"{language_definition} {additional_language_defintions}"
        return language_definition

    def generate_alter_session(self) -> str:
        return f"""ALTER SESSION SET SCRIPT_LANGUAGES='{self.generate_definition()}';"""

    def generate_alter_system(self) -> str:
        return f"""ALTER SYSTEM SET SCRIPT_LANGUAGES='{self.generate_definition()}';"""
