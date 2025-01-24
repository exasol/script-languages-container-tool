from typing import Dict

from exasol_integration_test_docker_environment.lib.docker.images.create.docker_image_create_task import (
    DockerCreateImageTask,
)
from exasol_integration_test_docker_environment.lib.docker.images.required_task_info import (
    RequiredTaskInfo,
)

import exasol.slc.internal.tasks.upload.deploy_containers
from exasol.slc.internal.tasks.upload.deploy_container_task import DeployContainerTask


class DeployContainerTasksCreator:

    def __init__(
        self,
        task: "exasol.slc.internal.tasks.upload.deploy_containers.DeployFlavorContainers",
    ) -> None:
        self.task = task

    def create_deploy_tasks(
        self, build_tasks: Dict[str, DockerCreateImageTask]
    ) -> Dict[str, DeployContainerTask]:
        return {
            release_goal: self._create_deploy_task(release_goal, build_task)
            for release_goal, build_task in build_tasks.items()
        }

    def _create_deploy_task(
        self, release_goal: str, build_task: DockerCreateImageTask
    ) -> DeployContainerTask:
        required_task_info = self._create_required_task_info(build_task)
        return self.task.create_child_task_with_common_params(
            DeployContainerTask,
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
