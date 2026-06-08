import os
from pathlib import Path

from exasol.slc.models.export_container_result import ExportContainerResult
from exasol.slc.models.export_info import ExportInfo


def assert_single_release_export(
    testcase,
    export_result: ExportContainerResult,
    export_dir: str,
    flavor_path: str,
    build_name: str | None = None,
) -> tuple[ExportInfo, Path]:
    testcase.assertEqual(len(export_result.export_infos), 1)
    export_infos_for_flavor = export_result.export_infos[flavor_path]
    testcase.assertEqual(len(export_infos_for_flavor), 1)
    export_info = export_infos_for_flavor["release"]

    exported_files = os.listdir(export_dir)
    assert export_info.output_file is not None
    export_path = Path(export_info.output_file)
    testcase.assertIn(export_path.name, exported_files)

    if build_name is not None:
        testcase.assertEqual(export_path.name, f"test-flavor_release_{build_name}.tar")
        testcase.assertIn(
            build_name, export_info.depends_on_image.get_target_complete_name()
        )
        testcase.assertNotIn(
            export_info.hash,
            export_info.depends_on_image.get_target_complete_name(),
        )
    else:
        testcase.assertIn(
            export_info.hash,
            export_info.depends_on_image.get_target_complete_name(),
        )

    return export_info, export_path
