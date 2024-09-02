import luigi

from exasol.slc.internal.tasks.upload.upload_container_parameter import (
    UploadContainerParameter,
)


class UploadContainersParameter(UploadContainerParameter):
    release_goals = luigi.ListParameter(["release"])
