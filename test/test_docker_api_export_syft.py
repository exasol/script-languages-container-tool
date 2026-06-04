import json
import os
import shutil
import subprocess
import tarfile
import unittest
from pathlib import Path

import docker
import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.testing import utils  # type: ignore

from exasol.slc import api
from exasol.slc.models.export_container_result import ExportContainerResult
from exasol.slc.models.export_info import ExportInfo


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

    def _assert_single_release_export(
        self, export_result: ExportContainerResult, build_name: str | None = None
    ) -> tuple[ExportInfo, Path]:
        flavor_path = str(exaslct_utils.get_test_flavor())
        self.assertEqual(len(export_result.export_infos), 1)
        export_infos_for_flavor = export_result.export_infos[flavor_path]
        self.assertEqual(len(export_infos_for_flavor), 1)
        export_info = export_infos_for_flavor["release"]

        exported_files = os.listdir(self.export_path)
        assert export_info.output_file is not None
        export_path = Path(export_info.output_file)
        self.assertIn(export_path.name, exported_files)

        if build_name is not None:
            self.assertEqual(export_path.name, f"test-flavor_release_{build_name}.tar")
            self.assertIn(
                build_name, export_info.depends_on_image.get_target_complete_name()
            )
            self.assertNotIn(
                export_info.hash,
                export_info.depends_on_image.get_target_complete_name(),
            )
        else:
            self.assertIn(
                export_info.hash,
                export_info.depends_on_image.get_target_complete_name(),
            )

        return export_info, export_path

    def _run_export(self, **kwargs) -> tuple[ExportContainerResult, Path]:
        export_result = api.export(
            flavor_path=(str(exaslct_utils.get_test_flavor()),),
            export_path=self.export_path,
            target_docker_repository_name=self.test_environment.docker_repository_name,
            force_rebuild=True,
            **kwargs,
        )
        _, export_path = self._assert_single_release_export(export_result)
        return export_result, export_path

    @classmethod
    def _ensure_syft_installed(cls) -> str:
        if cls._syft_binary is not None:
            return cls._syft_binary

        syft_binary = shutil.which("syft")
        if syft_binary is None:
            syft_install_dir = Path.home() / "bin"
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
