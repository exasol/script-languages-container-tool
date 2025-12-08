from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

class Accelerator(Enum):
    """
    This enum serves as a definition of values for possible accelerators for `run-db-tests`.
    """

    NONE = "none"
    NVIDA = "nvidia"


class TestSet(BaseModel):
    name: str
    files: list[str]
    folders: list[str]
    goal: str
    generic_language_tests: list[str]
    test_runner: Optional[str] = None
    accelerator: Accelerator = Accelerator.NONE


class TestConfig(BaseModel):
    default_test_runner: str
    test_sets: list[TestSet]


class FlavorCiConfig(BaseModel):
    build_runner: str
    test_config: TestConfig
