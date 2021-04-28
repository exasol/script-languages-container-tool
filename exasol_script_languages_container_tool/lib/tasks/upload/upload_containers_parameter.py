import luigi

from exasol_script_languages_container_tool.lib.tasks.upload.upload_container_parameter import UploadContainerParameter


class UploadContainersParameter(UploadContainerParameter):
    release_goals = luigi.ListParameter(["release"])
