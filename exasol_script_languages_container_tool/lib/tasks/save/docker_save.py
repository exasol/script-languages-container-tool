from typing import Dict

from exasol_integration_test_docker_environment.lib.base.flavor_task import FlavorsBaseTask
from exasol_integration_test_docker_environment.lib.docker.images.save.save_task_creator_for_build_tasks import \
    SaveTaskCreatorFromBuildTasks

from exasol_script_languages_container_tool.lib.tasks.build.docker_flavor_build_base import DockerFlavorBuildBase
from exasol_script_languages_container_tool.lib.tasks.save.docker_save_parameter import DockerSaveParameter


class DockerSave(FlavorsBaseTask, DockerSaveParameter):
    def __init__(self, *args, **kwargs):
        self.image_info_futures = None
        super().__init__(*args, **kwargs)

    def register_required(self):
        tasks = self.create_tasks_for_flavors_with_common_params(
            DockerFlavorSave)  # type: Dict[str,DockerFlavorSave]
        self.image_info_futures = self.register_dependencies(tasks)

    def run_task(self):
        image_infos = self.get_values_from_futures(self.image_info_futures)
        self.return_object(image_infos)


class DockerFlavorSave(DockerFlavorBuildBase, DockerSaveParameter):

    def get_goals(self):
        return self.goals

    def run_task(self):
        build_tasks = self.create_build_tasks(shortcut_build=not self.save_all)
        save_task_creator = SaveTaskCreatorFromBuildTasks(self)
        save_tasks = save_task_creator.create_tasks_for_build_tasks(build_tasks)
        image_info_futures = yield from self.run_dependencies(save_tasks)
        image_infos = self.get_values_from_futures(image_info_futures)
        self.return_object(image_infos)
