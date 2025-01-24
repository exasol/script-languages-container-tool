import luigi
from exasol_integration_test_docker_environment.lib.base.json_pickle_parameter import (
    JsonPickleParameter,
)

from exasol.slc.internal.tasks.test.upload_file_to_bucket_fs import UploadFileToBucketFS
from exasol.slc.models.export_info import ExportInfo


class UploadExportedContainer(UploadFileToBucketFS):
    release_name: str = luigi.Parameter()  # type: ignore
    release_goal: str = luigi.Parameter()  # type: ignore
    export_info: ExportInfo = JsonPickleParameter(ExportInfo, significant=False)  # type: ignore

    def get_log_file(self) -> str:
        return "/exa/logs/cored/bucketfsd*"

    def get_pattern_to_wait_for(self) -> str:
        return self.export_info.name + ".*extracted"  # pylint: disable=no-member

    def get_file_to_upload(self) -> str:
        file = self.export_info.cache_file  # pylint: disable=no-member
        return file

    def get_upload_target(self) -> str:
        return (
            "myudfs/" + self.export_info.name + ".tar.gz"  # pylint: disable=no-member
        )  # pylint: disable=no-member

    def get_sync_time_estimation(self) -> int:
        return 1 * 60
