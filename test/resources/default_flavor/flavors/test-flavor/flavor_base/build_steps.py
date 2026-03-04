from exasol.slc.internal.tasks.build.docker_flavor_image_task import (
    DockerFlavorAnalyzeImageTask,
)


class AnalyzeBuildRun(DockerFlavorAnalyzeImageTask):

    def get_build_step(self) -> str:
        return "build_run"

    def get_additional_build_directories_mapping(self) -> dict[str, str]:
        return {}

    def get_path_in_flavor(self):
        return "flavor_base"



class AnalyzeFlavorCustomization(DockerFlavorAnalyzeImageTask):

    def get_build_step(self) -> str:
        return "flavor_customization"

    def requires_tasks(self):
        return {"flavor_base_deps": AnalyzeBuildRun}



class AnalyzeRelease(DockerFlavorAnalyzeImageTask):
    def get_build_step(self) -> str:
        return "release"

    def requires_tasks(self):
        return {
            "flavor_customization": AnalyzeFlavorCustomization,
        }

    def get_path_in_flavor(self):
        return "flavor_base"

    def get_language_definition(self) -> str:
        return "language_definitions.json"


class SecurityScan(DockerFlavorAnalyzeImageTask):
    def get_build_step(self) -> str:
        return "security_scan"

    def requires_tasks(self):
        return {"release": AnalyzeRelease}

    def get_path_in_flavor(self):
        return "flavor_base"
