# pylint: disable=not-an-iterable
from collections.abc import Generator
from typing import Dict, List, Set, Tuple

import luigi
from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask
from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorsBaseTask,
)
from exasol_integration_test_docker_environment.lib.docker.images.image_info import (
    ImageInfo,
)
from exasol_integration_test_docker_environment.lib.docker.images.push.docker_push_parameter import (
    DockerPushParameter,
)
from exasol_integration_test_docker_environment.lib.docker.images.push.push_task_creator_for_build_tasks import (
    PushTaskCreatorFromBuildTasks,
)

from exasol.slc.internal.tasks.build.docker_flavor_build_base import (
    DockerFlavorBuildBase,
)


class DockerFlavorsPush(FlavorsBaseTask, DockerPushParameter):
    goals: tuple[str, ...] = luigi.ListParameter()  # type: ignore

    def __init__(self, *args, **kwargs) -> None:
        self.image_info_futures = None
        super().__init__(*args, **kwargs)

    def register_required(self) -> None:
        tasks: dict[
            str, DockerFlavorPush
        ] = self.create_tasks_for_flavors_with_common_params(
            DockerFlavorPush
        )  # type: ignore
        self.image_info_futures = self.register_dependencies(tasks)

    def run_task(self) -> None:
        image_infos: dict[str, list[ImageInfo]] = self.get_values_from_futures(
            self.image_info_futures
        )
        assert isinstance(image_infos, dict)
        assert all(isinstance(x, str) for x in image_infos.keys())
        assert all(isinstance(x, list) for x in image_infos.values())
        assert all(isinstance(y, ImageInfo) for x in image_infos.values() for y in x)

        self.return_object(image_infos)


class DockerFlavorPush(DockerFlavorBuildBase, DockerPushParameter):
    goals: tuple[str, ...] = luigi.ListParameter()  # type: ignore

    def __init__(self, *args, **kwargs) -> None:
        self.image_info_futures = None
        super().__init__(*args, **kwargs)

    def get_goals(self) -> set[str]:
        return set(self.goals)

    def run_task(self) -> Generator[BaseTask, None, None]:
        build_tasks = self.create_build_tasks(shortcut_build=not self.push_all)
        push_task_creator = PushTaskCreatorFromBuildTasks(self)
        push_tasks = push_task_creator.create_tasks_for_build_tasks(build_tasks)
        image_info_futures = yield from self.run_dependencies(push_tasks)
        image_infos: list[ImageInfo] = self.get_values_from_futures(image_info_futures)
        assert isinstance(image_infos, list)
        assert all(isinstance(x, ImageInfo) for x in image_infos)
        self.return_object(image_infos)
