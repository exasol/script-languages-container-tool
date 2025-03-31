from pathlib import Path

import luigi
from exasol_integration_test_docker_environment.lib.base.json_pickle_parameter import (
    JsonPickleParameter,
)

from exasol.slc.internal.tasks.test.upload_file_to_bucket_fs import UploadFileToBucketFS
from exasol.slc.models.export_info import ExportInfo


class UploadExportedContainer(UploadFileToBucketFS):
    file_to_upload: str = luigi.Parameter()  # type: ignore
    target_name: str = luigi.Parameter()  # type: ignore

    def get_log_file(self) -> str:
        return "/exa/logs/cored/bucketfsd*"

    def get_pattern_to_wait_for(self) -> str:
        return self.target_name + ".*extracted"  # pylint: disable=no-member

    def get_file_to_upload(self) -> str:
        return self.file_to_upload

    def get_upload_target(self) -> str:
        return (
            "myudfs/" + self.target_name + ".tar.gz"  # pylint: disable=no-member
        )  # pylint: disable=no-member

    def get_sync_time_estimation(self) -> int:
        return 1 * 60
