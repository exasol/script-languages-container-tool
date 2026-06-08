import json
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

import docker
import export_test_utils  # type: ignore[import-not-found]
import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.testing import utils  # type: ignore

from exasol.slc import api
from exasol.slc.models.export_container_result import ExportContainerResult


class ApiDockerExportSyftTest(unittest.TestCase):
    _syft_binary: str | None = None

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctApiTestEnvironmentWithCleanup(
            self, True
        )
        self.export_path = self.test_environment.temp_dir + "/export_dir"
        self.docker_client = docker.from_env()
        self.test_environment.clean_all_images()
        self.syft_binary = self._ensure_syft_installed()

    def tearDown(self):
        utils.close_environments(self.test_environment)

    def _run_export(self, **kwargs) -> tuple[ExportContainerResult, Path]:
        export_result = api.export(
            flavor_path=(str(exaslct_utils.get_test_flavor()),),
            export_path=self.export_path,
            target_docker_repository_name=self.test_environment.docker_repository_name,
            force_rebuild=True,
            **kwargs,
        )
        _, export_path = export_test_utils.assert_single_release_export(
            self,
            export_result,
            self.export_path,
            flavor_path=str(exaslct_utils.get_test_flavor()),
        )
        return export_result, export_path

    @classmethod
    def _ensure_syft_installed(cls) -> str:
        if cls._syft_binary is not None:
            return cls._syft_binary

        syft_binary = shutil.which("syft")
        if syft_binary is None:
            syft_install_dir = Path(tempfile.mkdtemp(prefix="syft-"))
            syft_install_dir.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                [
                    "bash",
                    "-lc",
                    "curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | "
                    f"sh -s -- -b {syft_install_dir}",
                ],
                check=True,
            )
            syft_binary = str(syft_install_dir / "syft")

        cls._syft_binary = syft_binary
        return syft_binary

    def _assert_dpkg_directory_is_present(self, export_archive: Path) -> None:
        with tarfile.open(export_archive, "r:*") as tf:
            tf_members = tf.getmembers()
            self.assertTrue(
                any(member.name.startswith("var/lib/dpkg/") for member in tf_members),
                "Expected var/lib/dpkg/ to be present in the exported archive.",
            )

    def _assert_syft_reports_deb_packages(self, export_archive: Path) -> None:
        completed_process = subprocess.run(
            [self.syft_binary, "scan", f"file:{export_archive}", "-o", "json"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed_process.stdout)
        artifacts = result["artifacts"]
        self.assertGreater(
            len(artifacts), 0, "Expected syft to report at least one package."
        )
        self.assertTrue(
            all(artifact["type"] == "deb" for artifact in artifacts),
            "Expected all syft packages to be Debian packages.",
        )

    def test_docker_export_keeps_dpkg_directory(self):
        _, export_path = self._run_export()
        self._assert_dpkg_directory_is_present(export_path)

    def test_docker_export_syft_reports_debian_packages(self):
        _, export_path = self._run_export()
        self._assert_syft_reports_deb_packages(export_path)


if __name__ == "__main__":
    unittest.main()
