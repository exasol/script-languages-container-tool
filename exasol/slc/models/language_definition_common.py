import datetime
from enum import Enum
from pathlib import PurePosixPath

from pydantic import BaseModel


class SLCLanguage(str, Enum):
    Java = "java"
    Python3 = "python"
    R = "r"


class SLCParameter(BaseModel):
    """
    Key value pair of a parameter passed to the Udf client. For example: `lang=java`
    """

    key: str
    value: str


class UdfClientRelativePath(BaseModel):
    """
    Path to the udf client relative to the Script Languages Container root path.
    For example `/exaudf/exaudfclient_py3`
    """

    executable: PurePosixPath

    def __str__(self) -> str:
        return str(self.executable)


class DeprecationInfo(BaseModel):
    """
    Deprecation info for the language.
    For example: deprecation_date="2024-10-31" default_changed_to="Java 17"
    """

    deprecation_date: datetime.date

    default_changed_to: str
