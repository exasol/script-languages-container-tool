from pydantic import BaseModel

from exasol.slc.models.accelerator import Accelerator


class TestSet(BaseModel):
    name: str
    files: list[str]
    folders: list[str]
    goal: str
    generic_language_tests: list[str]
    test_runners: list[str] | None = None
    accelerator: Accelerator = Accelerator.NONE


class TestConfig(BaseModel):
    default_test_runners: list[str]
    test_sets: list[TestSet]


class FlavorCiConfig(BaseModel):
    build_runners: list[str]
    test_config: TestConfig
