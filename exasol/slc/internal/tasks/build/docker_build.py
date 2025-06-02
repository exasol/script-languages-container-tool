# pylint: disable=not-an-iterable
from collections.abc import Generator
from typing import Dict, Optional, Set, Tuple

import luigi
from exasol_integration_test_docker_environment.lib.base.abstract_task_future import (
    AbstractTaskFuture,
)
from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask
from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorsBaseTask,
)
from exasol_integration_test_docker_environment.lib.docker.images.image_info import (
    ImageInfo,
)
from luigi import Config

from exasol.slc.internal.tasks.build.docker_flavor_build_base import (
    DockerFlavorBuildBase,
)


class DockerBuildParameter(Config):
    goals: tuple[str, ...] = luigi.ListParameter()  # type: ignore
    shortcut_build: bool = luigi.BoolParameter(True)  # type: ignore


class DockerBuild(FlavorsBaseTask, DockerBuildParameter):

    def __init__(self, *args, **kwargs) -> None:
        self._images_futures: Optional[AbstractTaskFuture] = None
        super().__init__(*args, **kwargs)

    def register_required(self) -> None:
        tasks = self.create_tasks_for_flavors_with_common_params(DockerFlavorBuild)
        self._images_futures = self.register_dependencies(tasks)

    def run_task(self) -> None:
        image_infos: dict[str, dict[str, ImageInfo]] = self.get_values_from_futures(
            self._images_futures
        )
        assert isinstance(image_infos, dict)
        assert all(isinstance(x, str) for x in image_infos.keys())
        assert all(isinstance(x, dict) for x in image_infos.values())
        assert all(isinstance(y, str) for x in image_infos.values() for y in x.keys())
        assert all(
            isinstance(y, ImageInfo) for x in image_infos.values() for y in x.values()
        )
        self.return_object(image_infos)


class DockerFlavorBuild(DockerFlavorBuildBase, DockerBuildParameter):

    def get_goals(self) -> set[str]:
        return set(self.goals)

    def run_task(self) -> Generator[BaseTask, None, None]:
        build_tasks = self.create_build_tasks(self.shortcut_build)
        image_info_futures = yield from self.run_dependencies(build_tasks)
        image_infos: dict[str, ImageInfo] = self.get_values_from_futures(
            image_info_futures
        )
        assert isinstance(image_infos, dict)
        assert all(isinstance(x, str) for x in image_infos.keys())
        assert all(isinstance(x, ImageInfo) for x in image_infos.values())
        self.return_object(image_infos)
