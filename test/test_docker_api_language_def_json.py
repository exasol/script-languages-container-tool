import datetime
import json
import shutil
import tarfile
import unittest
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory, tempdir

import docker  # type: ignore
import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.lib.docker.images.image_info import (
    ImageInfo,
)
from exasol_integration_test_docker_environment.testing import utils  # type: ignore
from pydantic import ValidationError

from exasol.slc.api import build
from exasol.slc.internal.utils.docker_utils import find_images_by_tag
from exasol.slc.models.language_definition_common import (
    DeprecationInfo,
    SLCLanguage,
    UdfClientRelativePath,
)
from exasol.slc.models.language_definition_model import (
    LanguageDefinition,
    LanguageDefinitionsModel,
)


class ApiDockerBuildLangDefJsonTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctApiTestEnvironmentWithCleanup(
            self, True
        )
        self.docker_client = docker.from_env()
        self.test_environment.clean_all_images()

    def tearDown(self):
        try:
            self.docker_client.close()
        except Exception as e:
            print(e)

        utils.close_environments(self.test_environment)

    def read_file_from_docker_image(self, image_name, file_path):
        # Create a container from the image
        container = self.docker_client.containers.create(
            image_name, command="sleep infinity", detach=True
        )

        try:
            # Start the container
            container.start()

            # Copy the file from the container to host
            tar_stream, _ = container.get_archive(file_path)

            # Extract the file content from the tar stream
            import io

            file_content = None

            with TemporaryDirectory() as d:
                tar_file_path = Path(d) / "tmp.tar"
                self.write_tar_file(tar_file_path, tar_stream)
                file_content = self.read_tar_file_content(file_content, tar_file_path)

            return file_content.decode("utf-8") if file_content else None

        finally:
            # Stop and remove the container
            container.stop()
            container.remove()

    def write_tar_file(self, tar_file_path, tar_stream):
        with open(tar_file_path, "wb") as f:
            for chunk in tar_stream:
                f.write(chunk)

    def read_tar_file_content(self, file_content, tar_file_path):
        with tarfile.open(tar_file_path) as tar:
            for member in tar.getmembers():
                f = tar.extractfile(member)
                if f:
                    file_content = f.read()
                    break
        return file_content

    def test_docker_build(self) -> None:
        flavor_path = exaslct_utils.get_test_flavor()
        image_infos = build(
            flavor_path=(str(flavor_path),),
            source_docker_repository_name=self.test_environment.docker_repository_name,
            target_docker_repository_name=self.test_environment.docker_repository_name,
        )
        assert len(image_infos) == 1
        images = find_images_by_tag(
            self.docker_client,
            lambda tag: tag.startswith(self.test_environment.docker_repository_name),
        )
        self.assertTrue(
            len(images) > 0,
            f"Did not found images for repository "
            f"{self.test_environment.docker_repository_name} in list {images}",
        )
        print("image_infos", image_infos.keys())
        image_infos_for_test_flavor = image_infos[str(flavor_path)]
        image_info: ImageInfo = image_infos_for_test_flavor["release"]

        expected_prefix = f"{image_info.target_repository_name}:{image_info.target_tag}"
        images = find_images_by_tag(
            self.docker_client, lambda tag: tag.startswith(expected_prefix)
        )
        self.assertTrue(
            len(images) == 1,
            f"Did not found image for goal 'release' with prefix {expected_prefix} in list {images}",
        )

        lang_def_json = self.read_file_from_docker_image(
            images[0].id, "build_info/language_definitions.json"
        )
        model = LanguageDefinitionsModel.model_validate_json(lang_def_json)
        print(model)

        self.assertEqual(
            model,
            LanguageDefinitionsModel(
                schema_version=1,
                language_definitions=[
                    LanguageDefinition(
                        protocol="localzmq+protobuf",
                        aliases=["JAVA"],
                        language=SLCLanguage.Java,
                        udf_client_path=UdfClientRelativePath(
                            executable=PurePosixPath("/exaudf/exaudfclient")
                        ),
                        parameters=[],
                        deprecation=DeprecationInfo(
                            deprecation_date=datetime.datetime(2024, 10, 31),
                            default_changed_to="Java 17",
                        ),
                    )
                ],
            ),
        )

    def test_docker_build_invalid_lang_def_json(self):
        flavor_path = exaslct_utils.get_test_flavor()
        with TemporaryDirectory() as d:
            temp_flavor_path = Path(d) / "test_flavor"
            shutil.copytree(flavor_path, temp_flavor_path)

            lang_def_json_path = (
                temp_flavor_path / "flavor_base" / "language_definitions.json"
            )
            orig_lang_def_json = lang_def_json_path.read_text()
            lang_def_invalid = json.loads(orig_lang_def_json)
            lang_def_invalid.update({"language_definitions": "abc"})
            with open(lang_def_json_path, "w") as f:
                f.write(json.dumps(lang_def_invalid))

            self.assertRaises(
                ValidationError,
                build,
                flavor_path=(str(temp_flavor_path),),
                source_docker_repository_name=self.test_environment.docker_repository_name,
                target_docker_repository_name=self.test_environment.docker_repository_name,
            )

    def test_docker_build_without_deprecation_info(self):
        flavor_path = exaslct_utils.get_test_flavor()
        with TemporaryDirectory() as d:
            temp_flavor_path = Path(d) / "test_flavor"
            shutil.copytree(flavor_path, temp_flavor_path)

            lang_def_json_path = (
                temp_flavor_path / "flavor_base" / "language_definitions.json"
            )
            orig_lang_def_json = lang_def_json_path.read_text()
            lang_def_invalid = json.loads(orig_lang_def_json)
            lang_def_invalid["language_definitions"][0].update({"deprecation": None})
            with open(lang_def_json_path, "w") as f:
                f.write(json.dumps(lang_def_invalid))

            image_infos = build(
                flavor_path=(str(temp_flavor_path),),
                source_docker_repository_name=self.test_environment.docker_repository_name,
                target_docker_repository_name=self.test_environment.docker_repository_name,
            )

        assert len(image_infos) == 1
        images = find_images_by_tag(
            self.docker_client,
            lambda tag: tag.startswith(self.test_environment.docker_repository_name),
        )
        self.assertTrue(
            len(images) > 0,
            f"Did not found images for repository "
            f"{self.test_environment.docker_repository_name} in list {images}",
        )
        print("image_infos", image_infos.keys())
        image_infos_for_test_flavor = image_infos[str(temp_flavor_path)]
        image_info: ImageInfo = image_infos_for_test_flavor["release"]

        expected_prefix = f"{image_info.target_repository_name}:{image_info.target_tag}"
        images = find_images_by_tag(
            self.docker_client, lambda tag: tag.startswith(expected_prefix)
        )
        self.assertTrue(
            len(images) == 1,
            f"Did not found image for goal 'release' with prefix {expected_prefix} in list {images}",
        )

        lang_def_json = self.read_file_from_docker_image(
            images[0].id, "build_info/language_definitions.json"
        )
        model = LanguageDefinitionsModel.model_validate_json(lang_def_json)
        print(model)

        self.assertEqual(
            model,
            LanguageDefinitionsModel(
                schema_version=1,
                language_definitions=[
                    LanguageDefinition(
                        protocol="localzmq+protobuf",
                        aliases=["JAVA"],
                        language=SLCLanguage.Java,
                        udf_client_path=UdfClientRelativePath(
                            executable=PurePosixPath("/exaudf/exaudfclient")
                        ),
                        parameters=[],
                        deprecation=None,
                    )
                ],
            ),
        )


if __name__ == "__main__":
    unittest.main()
