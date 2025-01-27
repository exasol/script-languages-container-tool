import importlib
from typing import Any

import luigi
from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask
from exasol_integration_test_docker_environment.lib.base.json_pickle_parameter import (
    JsonPickleParameter,
)
from exasol_integration_test_docker_environment.lib.docker.images.required_task_info import (
    RequiredTaskInfo,
)

from exasol.slc.internal.tasks.upload.upload_container_base_task import (
    UploadContainerBaseTask,
)


class UploadContainerTask(UploadContainerBaseTask):
    # We need to create the ExportContainerTask for UploadContainerTask dynamically,
    # because we want to push as soon as possible after an image was build and
    # don't want to wait for the push finishing before starting the build of depended images,
    # but we also need to create a UploadContainerTask for each ExportContainerTask of a goal

    required_task_info: RequiredTaskInfo = JsonPickleParameter(
        RequiredTaskInfo,
        visibility=luigi.parameter.ParameterVisibility.HIDDEN,
        significant=True,
    )  # type: ignore

    def get_export_task(self) -> BaseTask:
        module = importlib.import_module(
            self.required_task_info.module_name  # pylint: disable=no-member
        )
        class_ = getattr(
            module, self.required_task_info.class_name  # pylint: disable=no-member
        )
        instance = self.create_child_task(
            class_, **self.required_task_info.params  # pylint: disable=no-member
        )
        return instance
