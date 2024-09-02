import luigi
from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorsBaseTask,
)
from exasol_integration_test_docker_environment.lib.base.json_pickle_target import (
    JsonPickleTarget,
)
from exasol_integration_test_docker_environment.lib.base.pickle_target import (
    PickleTarget,
)
from luigi import Config
from luigi.format import Nop

from exasol.slc.internal.tasks.build.docker_flavor_build_base import (
    DockerFlavorBuildBase,
)


class DockerBuildParameter(Config):
    goals = luigi.ListParameter()
    shortcut_build = luigi.BoolParameter(True)


class DockerBuild(FlavorsBaseTask, DockerBuildParameter):

    def __init__(self, *args, **kwargs):
        self._images_futures = None
        super().__init__(*args, **kwargs)

    def register_required(self):
        tasks = self.create_tasks_for_flavors_with_common_params(DockerFlavorBuild)
        self._images_futures = self.register_dependencies(tasks)

    def run_task(self):
        image_info = self.get_values_from_futures(self._images_futures)
        self.return_object(image_info)


class DockerFlavorBuild(DockerFlavorBuildBase, DockerBuildParameter):

    def get_goals(self):
        return self.goals

    def run_task(self):
        build_tasks = self.create_build_tasks(self.shortcut_build)
        image_info_futures = yield from self.run_dependencies(build_tasks)
        image_infos = self.get_values_from_futures(image_info_futures)
        self.return_object(image_infos)
