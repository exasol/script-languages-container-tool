from pathlib import PurePath

import luigi
from exasol_integration_test_docker_environment.lib.test_environment.database_setup.populate_data import (
    PopulateTestDataToDatabase,
)

from exasol.slc.internal.tasks.test.test_container_content import TEST_DATA_TARGET


class PopulateTestEngine(PopulateTestDataToDatabase):

    def get_data_path_within_test_container(self) -> PurePath:
        return PurePath(TEST_DATA_TARGET) / "enginedb_small"

    def get_data_file_within_data_path(self) -> PurePath:
        return PurePath("import.sql")
