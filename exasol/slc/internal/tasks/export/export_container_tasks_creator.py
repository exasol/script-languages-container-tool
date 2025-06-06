from typing import Dict, Optional

from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask
from exasol_integration_test_docker_environment.lib.docker.images.create.docker_image_create_task import (
    DockerCreateImageTask,
)
from exasol_integration_test_docker_environment.lib.docker.images.required_task_info import (
    RequiredTaskInfo,
)

from exasol.slc.internal.tasks.export.export_container_task import ExportContainerTask


class ExportContainerTasksCreator:

    def __init__(self, task: BaseTask, export_path: Optional[str]):
        self.export_path = export_path
        self.task = task

    def create_export_tasks(
        self, build_tasks: dict[str, DockerCreateImageTask]
    ) -> dict[str, ExportContainerTask]:
        return {
            release_goal: self._create_export_task(release_goal, build_task)
            for release_goal, build_task in build_tasks.items()
        }

    def _create_export_task(
        self, release_goal: str, build_task: DockerCreateImageTask
    ) -> ExportContainerTask:
        required_task_info = self._create_required_task_info(build_task)
        return self.task.create_child_task_with_common_params(
            ExportContainerTask,
            export_path=self.export_path,
            required_task_info=required_task_info,
            release_goal=release_goal,
        )

    @staticmethod
    def _create_required_task_info(build_task) -> RequiredTaskInfo:
        required_task_info = RequiredTaskInfo(
            module_name=build_task.__module__,
            class_name=build_task.__class__.__name__,
            params=build_task.param_kwargs,
        )
        return required_task_info
