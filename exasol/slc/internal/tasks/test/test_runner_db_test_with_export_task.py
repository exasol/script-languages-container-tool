from typing import Dict

from exasol.slc.internal.tasks.export.export_container_parameters import (
    ExportContainerOptionsParameter,
)
from exasol.slc.internal.tasks.export.export_containers import ExportFlavorContainer
from exasol.slc.internal.tasks.test.container_file_under_test_info import (
    ContainerFileUnderTestInfo,
)
from exasol.slc.internal.tasks.test.test_runner_db_test_base_task import (
    TestRunnerDBTestBaseTask,
)
from exasol.slc.models.export_info import ExportInfo


class TestRunnerDBTestWithExportTask(
    TestRunnerDBTestBaseTask, ExportContainerOptionsParameter
):

    def register_required(self) -> None:
        self.register_export_container()
        self.register_spawn_test_environment()

    def register_export_container(self) -> None:
        export_container_task = self.create_child_task(
            ExportFlavorContainer,
            release_goals=[self.release_goal],
            flavor_path=self.flavor_path,
            compression_strategy=self.compression_strategy,
        )
        self._export_infos_future = self.register_dependency(export_container_task)

    def _get_container_file_under_test_info(self) -> ContainerFileUnderTestInfo:

        export_infos: dict[str, ExportInfo] = self.get_values_from_future(
            self._export_infos_future
        )  # type: ignore
        assert isinstance(export_infos, dict)
        assert all(isinstance(x, str) for x in export_infos.keys())
        assert all(isinstance(x, ExportInfo) for x in export_infos.values())

        export_info = export_infos[self.release_goal]
        return ContainerFileUnderTestInfo(
            container_file=export_info.cache_file,
            target_name=export_info.name,
            is_new=export_info.is_new,
        )
