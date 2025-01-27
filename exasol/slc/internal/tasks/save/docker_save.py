# pylint: disable=not-an-iterable
from typing import Dict, Generator, List, Set

from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask
from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorsBaseTask,
)
from exasol_integration_test_docker_environment.lib.docker.images.image_info import (
    ImageInfo,
)
from exasol_integration_test_docker_environment.lib.docker.images.save.save_task_creator_for_build_tasks import (
    SaveTaskCreatorFromBuildTasks,
)

from exasol.slc.internal.tasks.build.docker_flavor_build_base import (
    DockerFlavorBuildBase,
)
from exasol.slc.internal.tasks.save.docker_save_parameter import DockerSaveParameter


class DockerSave(FlavorsBaseTask, DockerSaveParameter):
    def __init__(self, *args, **kwargs) -> None:
        self.image_info_futures = None
        super().__init__(*args, **kwargs)

    def register_required(self) -> None:
        tasks: Dict[str, DockerFlavorSave] = self.create_tasks_for_flavors_with_common_params(  # type: ignore
            DockerFlavorSave
        )  # type: ignore
        self.image_info_futures = self.register_dependencies(tasks)

    def run_task(self) -> None:
        image_infos: Dict[str, List[ImageInfo]] = self.get_values_from_futures(
            self.image_info_futures
        )
        assert isinstance(image_infos, dict)
        assert all(isinstance(x, str) for x in image_infos.keys())
        assert all(isinstance(y, ImageInfo) for x in image_infos.values() for y in x)
        self.return_object(image_infos)


class DockerFlavorSave(DockerFlavorBuildBase, DockerSaveParameter):

    def get_goals(self) -> Set[str]:
        return set(self.goals)

    def run_task(self) -> Generator[BaseTask, None, None]:
        build_tasks = self.create_build_tasks(shortcut_build=not self.save_all)
        save_task_creator = SaveTaskCreatorFromBuildTasks(self)
        save_tasks = save_task_creator.create_tasks_for_build_tasks(build_tasks)
        image_info_futures = yield from self.run_dependencies(save_tasks)
        image_infos: List[ImageInfo] = self.get_values_from_futures(image_info_futures)
        assert isinstance(image_infos, list)
        assert all(isinstance(x, ImageInfo) for x in image_infos)
        self.return_object(image_infos)
