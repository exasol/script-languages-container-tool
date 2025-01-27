# pylint: disable=not-an-iterable
from typing import Dict, Generator, Set

from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask
from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorsBaseTask,
)

from exasol.slc.internal.tasks.build.docker_flavor_build_base import (
    DockerFlavorBuildBase,
)
from exasol.slc.internal.tasks.export.export_container_task import ExportContainerTask
from exasol.slc.internal.tasks.export.export_container_tasks_creator import (
    ExportContainerTasksCreator,
)
from exasol.slc.internal.tasks.upload.deploy_container_task import DeployContainerTask
from exasol.slc.internal.tasks.upload.deploy_container_tasks_creator import (
    DeployContainerTasksCreator,
)
from exasol.slc.internal.tasks.upload.upload_containers_parameter import (
    UploadContainersParameter,
)


class DeployContainers(FlavorsBaseTask, UploadContainersParameter):

    def __init__(self, *args, **kwargs) -> None:
        self.lang_def_builders_futures = None
        super().__init__(*args, **kwargs)

    def register_required(self) -> None:
        tasks: Dict[str, DeployFlavorContainers] = (
            self.create_tasks_for_flavors_with_common_params(DeployFlavorContainers)
        )
        self.lang_def_builders_futures = self.register_dependencies(tasks)

    def run_task(self) -> None:
        lang_definitionbuilders = self.get_values_from_futures(
            self.lang_def_builders_futures
        )
        self.return_object(lang_definitionbuilders)


class DeployFlavorContainers(DockerFlavorBuildBase, UploadContainersParameter):

    def get_goals(self) -> Set[str]:
        return set(self.release_goals)

    def run_task(self) -> Generator[BaseTask, None, None]:
        build_tasks = self.create_build_tasks()

        export_tasks = self.create_export_tasks(build_tasks)
        deploy_tasks = self.create_deploy_tasks(export_tasks)

        lang_definitions_futures = yield from self.run_dependencies(deploy_tasks)
        language_definition = self.get_values_from_futures(lang_definitions_futures)
        self.return_object(language_definition)

    def create_deploy_tasks(self, export_tasks) -> Dict[str, DeployContainerTask]:
        deploy_tasks_creator = DeployContainerTasksCreator(self)
        deploy_tasks = deploy_tasks_creator.create_deploy_tasks(export_tasks)
        return deploy_tasks

    def create_export_tasks(self, build_tasks) -> Dict[str, ExportContainerTask]:
        export_tasks_creator = ExportContainerTasksCreator(self, export_path=None)
        export_tasks = export_tasks_creator.create_export_tasks(build_tasks)
        return export_tasks
