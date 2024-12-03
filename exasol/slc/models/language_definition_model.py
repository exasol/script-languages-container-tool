from dataclasses import dataclass
from typing import Annotated, List

from pydantic import BaseModel, Field

from exasol.slc.models.language_definition_common import (
    SLCLanguage,
    SLCParameter,
    UdfClientRelativePath,
)


class LanguageDefinition(BaseModel):
    """
    Contains information about a supported language and the respective path of the UDF client of an Script-Languages-Container.
    """

    protocol: str
    aliases: List[str]
    language: SLCLanguage
    parameters: List[SLCParameter]
    udf_client_path: UdfClientRelativePath


class LanguageDefinitionsModel(BaseModel):
    """
    Contains information about all supported languages and the respective path of the UDF client of an Script-Languages-Container.
    """

    language_definitions: List[LanguageDefinition]
