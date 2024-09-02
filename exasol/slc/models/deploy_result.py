from attr import dataclass

from exasol.slc.models.language_definitions_builder import LanguageDefinitionsBuilder


@dataclass
class DeployResult:
    release_path: str
    upload_url: str
    language_definition_builder: LanguageDefinitionsBuilder
