from typing import Dict, List, Optional

import luigi
from exasol_integration_test_docker_environment.lib.base.json_pickle_parameter import (
    JsonPickleParameter,
)
from exasol_integration_test_docker_environment.lib.data.environment_info import (
    EnvironmentInfo,
)


class GeneralRunDBTestParameter:
    test_restrictions: List[str] = luigi.ListParameter([])  # type: ignore
    test_environment_vars: Dict[str, str] = luigi.DictParameter({}, significant=False)  # type: ignore
    test_log_level: str = luigi.Parameter("critical", significant=False)  # type: ignore


class ActualRunDBTestParameter(GeneralRunDBTestParameter):
    release_goal: str = luigi.Parameter()  # type: ignore
    language_definition: str = luigi.Parameter(significant=False)  # type: ignore
    test_environment_info: EnvironmentInfo = JsonPickleParameter(
        EnvironmentInfo, significant=False
    )  # type: ignore


class RunDBTestParameter(ActualRunDBTestParameter):
    language: Optional[str] = luigi.OptionalParameter()  # type: ignore


class RunDBGenericLanguageTestParameter(GeneralRunDBTestParameter):
    generic_language_tests: List[str] = luigi.ListParameter([])  # type: ignore


class RunDBLanguageTestParameter(GeneralRunDBTestParameter):
    languages: List[Optional[str]] = luigi.ListParameter([None])  # type: ignore


class RunDBTestFolderParameter(RunDBLanguageTestParameter):
    test_folders: List[str] = luigi.ListParameter([])  # type: ignore


class RunDBTestFilesParameter(RunDBLanguageTestParameter):
    test_files: List[str] = luigi.ListParameter([])  # type: ignore


class RunDBTestsInTestConfigParameter(
    RunDBGenericLanguageTestParameter, RunDBTestFolderParameter, RunDBTestFilesParameter
):
    pass
