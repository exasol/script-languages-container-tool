import exasol.bucketfs as bfs  # type: ignore
from attr import dataclass

from exasol.slc.models.language_definitions_builder import LanguageDefinitionsBuilder


@dataclass
class DeployResult:
    release_path: str
    human_readable_upload_location: str
    bucket_path: bfs.path.PathLike
    language_definition_builder: LanguageDefinitionsBuilder
