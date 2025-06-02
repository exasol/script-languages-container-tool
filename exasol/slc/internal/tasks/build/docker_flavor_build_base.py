from typing import Dict, List, Set

from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorBaseTask,
)
from exasol_integration_test_docker_environment.lib.docker.images.create.docker_build_base import (
    DockerBuildBase,
)
from exasol_integration_test_docker_environment.lib.docker.images.create.docker_image_analyze_task import (
    DockerAnalyzeImageTask,
)

from exasol.slc.internal.tasks.build.docker_flavor_image_task import (
    DockerFlavorAnalyzeImageTask,
)


class DockerFlavorBuildBase(FlavorBaseTask, DockerBuildBase):

    # TODO order pull for images which share dependencies

    # pylint: disable=no-member
    def get_goal_class_map(self) -> dict[str, DockerAnalyzeImageTask]:
        flavor_path: str = self.flavor_path  # type: ignore
        module_name_for_build_steps = flavor_path.replace("/", "_").replace(".", "_")
        available_tasks = [
            self.create_child_task_with_common_params(subclass)
            for subclass in DockerFlavorAnalyzeImageTask.__subclasses__()
            if subclass.__module__ == module_name_for_build_steps
        ]
        goal_class_map: dict[str, DockerAnalyzeImageTask] = {
            task.get_build_step(): task for task in available_tasks
        }
        return goal_class_map

    def get_default_goals(self) -> set[str]:
        goals = {"release", "base_test_build_run", "flavor_test_build_run"}
        return goals
