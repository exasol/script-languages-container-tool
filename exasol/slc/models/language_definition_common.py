from dataclasses import dataclass
from enum import Enum
from pathlib import PurePosixPath
from typing import List

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
    value: List[str]


class UdfClientRelativePath(BaseModel):
    """
    Path to the udf client relative to the Script Languages Container root path.
    For example `/exaudf/exaudfclient_py3`
    """

    executable: PurePosixPath

    def __str__(self) -> str:
        return str(self.executable)
