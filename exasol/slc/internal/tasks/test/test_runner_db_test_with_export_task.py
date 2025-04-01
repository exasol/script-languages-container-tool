from typing import Dict

from exasol.slc.internal.tasks.export.export_containers import ExportFlavorContainer
from exasol.slc.internal.tasks.test.test_container_file_info import (
    TestContainerFileInfo,
)
from exasol.slc.internal.tasks.test.test_runner_db_test_base_task import (
    TestRunnerDBTestBaseTask,
)
from exasol.slc.models.export_info import ExportInfo


class TestRunnerDBTestWithExportTask(TestRunnerDBTestBaseTask):

    def register_required(self) -> None:
        self.register_export_container()
        self.register_spawn_test_environment()

    def register_export_container(self) -> None:
        export_container_task = self.create_child_task(
            ExportFlavorContainer,
            release_goals=[self.release_goal],
            flavor_path=self.flavor_path,
        )
        self._export_infos_future = self.register_dependency(export_container_task)

    def get_test_container_file_info(self) -> TestContainerFileInfo:

        export_infos: Dict[str, ExportInfo] = self.get_values_from_future(
            self._export_infos_future
        )  # type: ignore
        assert isinstance(export_infos, dict)
        assert all(isinstance(x, str) for x in export_infos.keys())
        assert all(isinstance(x, ExportInfo) for x in export_infos.values())

        export_info = export_infos[self.release_goal]
        return TestContainerFileInfo(
            container_file=export_info.cache_file,
            target_name=export_info.name,
            is_new=export_info.is_new,
        )
