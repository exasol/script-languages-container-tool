from pathlib import Path

import yaml
from exasol.exaslpm.model.package_file_config import (
    CURRENT_VERSION as CURRENT_PACKAGE_VERSION,
)
from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    PackageFile,
)
from exasol.exaslpm.pkg_mgmt.package_file_session import PackageFileSession
from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorBaseTask,
)
from exasol_integration_test_docker_environment.lib.docker.images.create.docker_image_analyze_task import (
    DockerAnalyzeImageTask,
)
from exasol_integration_test_docker_environment.lib.models.config.build_config import (
    build_config,
)
from exasol_integration_test_docker_environment.lib.models.config.docker_config import (
    source_docker_repository_config,
    target_docker_repository_config,
)

from exasol.slc.models.language_definition_model import (
    LANGUAGE_DEFINITON_SCHEMA_VERSION,
    LanguageDefinitionsModel,
)
from exasol.slc.models.package_file_location import (
    PACKAGE_FILE_NAME,
    PackageFileLocation,
)


def sort_all_channels(obj):
    """
    Workaround until https://github.com/exasol/script-languages-package-management/issues/109 gets fixed.
    Channels are in undefined order, so this function recursively traverses the dictionary and sorts all occurrences
    of "channels".
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "channels" and isinstance(v, list):
                v.sort()
            else:
                sort_all_channels(v)
    elif isinstance(obj, list):
        for item in obj:
            sort_all_channels(item)
    return obj


def package_model_to_yaml_str(model: PackageFile) -> str:
    """
    Converts the given PackageFile model to a YAML string.
    The method might reorder the keys (sort_keys=True) in order to provide a reproducible result.
    Note: Uses (mode="JSON") for correct serialization of `Path` objects.
    """
    d = model.model_dump(mode="json", exclude_none=True)
    sort_all_channels(d)
    return yaml.dump(d, sort_keys=True)


class DockerFlavorAnalyzeImageTask(DockerAnalyzeImageTask, FlavorBaseTask):
    # TODO change task inheritance with composition.
    #  In this case DockerPullOrBuildFlavorImageTask could create a DockerPullOrBuildImageTask
    #  if this would have parameters instead of abstract methods

    def __init__(self, *args, **kwargs) -> None:
        self.build_step = (  # pylint: disable=assignment-from-no-return
            self.get_build_step()
        )
        self.additional_build_directories_mapping = (
            self.get_additional_build_directories_mapping()
        )
        super().__init__(*args, **kwargs)

    def is_rebuild_requested(self) -> bool:
        config = build_config()
        return config.force_rebuild and (
            self.get_build_step() in config.force_rebuild_from
            or len(config.force_rebuild_from) == 0
        )

    def get_build_step(self) -> str:
        """
        Called by the constructor to get the name of build step.
        Sub classes need to implement this method.
        :return: dictionaries with destination path as keys and source paths in values
        """
        return ""

    def get_additional_build_directories_mapping(self) -> dict[str, str]:
        """
        Called by the constructor to get additional build directories or files which are specific to the build step.
        This mappings gets merged with the default flavor build directories mapping.
        The keys are the relative paths to the destination in build context and
        the values are the paths to the source directories or files.
        Sub classes need to implement this method.
        :return: dictionaries with destination path as keys and source paths in values
        """
        return {}

    def get_language_definition(self) -> str:
        """
        Called by the constructor to get a language definition file which will be validated against
        the language definition JSON Schema and (if validations succeeded) copied to the temporary build directory.
        :return: string with source path of language definition JSON or an empty string
        """
        return ""

    def get_path_in_flavor(self) -> Path | None:
        """
        Called by the constructor to get the path to the build context of the build step within the flavor path.
        Sub classes need to implement this method.
        :return: dictionaries with destination path as keys and source paths in values
        """
        return None

    def get_package_file_name(self) -> str:
        """
        Returns the package file name of the automatically generated packages file, which will be created in the docker image.
        Sub classes can override this value to customize the package file name.
        """
        return f"{self.build_step}_{PACKAGE_FILE_NAME}"

    def get_additional_resources(self) -> dict[str, str]:
        """
        Called by the constructor to get additional resources for the docker build.
        For each entry of the dict the base class will generate a new file, with the value of the dict as content.
        Sub-classes need to implement this method.
        :return: dictionary for additional resources.
        """
        package_file_name = self.get_package_file_name()
        build_step_package_file = self._build_package_file_for_current_build_step()
        ret_val = {}
        if build_step_package_file:
            ret_val[package_file_name] = package_model_to_yaml_str(
                build_step_package_file
            )
        return ret_val

    def get_source_repository_name(self) -> str:
        return source_docker_repository_config().repository_name  # type: ignore

    def get_target_repository_name(self) -> str:
        return target_docker_repository_config().repository_name  # type: ignore

    def get_source_image_tag(self) -> str:
        if source_docker_repository_config().tag_prefix != "":
            return (
                f"{source_docker_repository_config().tag_prefix}_{self.get_image_tag()}"
            )
        else:
            return f"{self.get_image_tag()}"

    def get_target_image_tag(self) -> str:
        if target_docker_repository_config().tag_prefix != "":
            return (
                f"{target_docker_repository_config().tag_prefix}_{self.get_image_tag()}"
            )
        else:
            return f"{self.get_image_tag()}"

    def get_image_tag(self) -> str:
        flavor_name = self.get_flavor_name()
        return f"{flavor_name}-{self.build_step}"

    def get_mapping_of_build_files_and_directories(self) -> dict[str, str]:
        build_step_path = self.get_build_step_path()
        assert self.build_step is not None
        result: dict[str, str] = {self.build_step: str(build_step_path)}
        result.update(self.additional_build_directories_mapping)
        if language_definition := self.get_language_definition():
            lang_def_path = self.get_path_in_flavor_path() / language_definition
            model = LanguageDefinitionsModel.model_validate_json(
                lang_def_path.read_text(), strict=True
            )
            if model.schema_version != LANGUAGE_DEFINITON_SCHEMA_VERSION:
                raise RuntimeError(
                    f"Unsupported schema version. Version from JSON: {model.schema_version}. Expected: {LANGUAGE_DEFINITON_SCHEMA_VERSION}"
                )
            result.update({"language_definitions.json": str(lang_def_path)})
        return result

    def get_build_step_path(self) -> Path:
        if build_step_path := self.get_build_step():
            return self.get_path_in_flavor_path() / build_step_path
        else:
            return self.get_path_in_flavor_path()

    def get_path_in_flavor_path(self) -> Path:
        flavor_path: str = self.flavor_path  # type: ignore
        if path_in_flavor := self.get_path_in_flavor():
            return Path(flavor_path) / path_in_flavor
        else:
            return Path(flavor_path)

    def get_dockerfile(self) -> str:
        return str(self.get_build_step_path().joinpath("Dockerfile"))

    def _find_build_step_in_packages_file(
        self, packages_file: Path
    ) -> BuildStep | None:
        if packages_file.is_file():
            pkg_file_session = PackageFileSession(packages_file)
            return pkg_file_session.package_file_config.find_build_step(
                self.build_step, raise_if_not_found=False
            )
        return None

    def _build_package_file_for_current_build_step(self) -> PackageFile | None:
        flavor_path = str(self.flavor_path)
        package_file_location = PackageFileLocation(flavor_path=Path(flavor_path))
        public_pkg_file = package_file_location.public_package_file
        internal_pkg_file = package_file_location.internal_package_file
        build_step_pkgs = self._find_build_step_in_packages_file(
            public_pkg_file
        ) or self._find_build_step_in_packages_file(internal_pkg_file)
        if not build_step_pkgs:
            return None
        return PackageFile(
            build_steps=[build_step_pkgs],
            comment=f"Automatically generated package file for build step {self.build_step}",
            version=CURRENT_PACKAGE_VERSION,
        )
