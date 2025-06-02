from dataclasses import dataclass
from typing import List, Optional

from pydantic import BaseModel

from exasol.slc.models.language_definition_common import (
    DeprecationInfo,
    SLCLanguage,
    SLCParameter,
    UdfClientRelativePath,
)

LANGUAGE_DEFINITON_SCHEMA_VERSION = 2


class LanguageDefinition(BaseModel):
    """
    Contains information about a supported language and the respective path of the UDF client of an Script-Languages-Container.
    """

    protocol: str
    aliases: list[str]
    parameters: list[SLCParameter]
    udf_client_path: UdfClientRelativePath
    deprecation: Optional[DeprecationInfo]


class LanguageDefinitionsModel(BaseModel):
    """
    Contains information about all supported languages and the respective path of the UDF client of an Script-Languages-Container.
    """

    schema_version: int

    language_definitions: list[LanguageDefinition]
