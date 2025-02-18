from typing import Generator, List

import docker.models.images
import luigi
from docker import DockerClient
from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask
from exasol_integration_test_docker_environment.lib.base.docker_base_task import (
    DockerBaseTask,
)
from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorBaseTask,
    FlavorsBaseTask,
)
from exasol_integration_test_docker_environment.lib.models.config.docker_config import (
    target_docker_repository_config,
)

from exasol.slc.internal.utils.docker_utils import find_images_by_tag


class CleanImageTask(DockerBaseTask):
    image_id: str = luigi.Parameter()  # type: ignore

    def run_task(self) -> Generator[BaseTask, None, None]:
        self.logger.info("Try to remove dependent images of %s" % self.image_id)
        yield from self.run_dependencies(
            self.get_clean_image_tasks_for_dependent_images()
        )
        for _ in range(3):
            try:
                with self._get_docker_client() as docker_client:
                    self.logger.info("Try to remove image %s" % self.image_id)
                    docker_client.images.remove(image=self.image_id, force=True)
                    self.logger.info("Removed image %s" % self.image_id)
                break
            except Exception as e:
                self.logger.info(
                    "Could not removed image {} got exception {}".format(
                        self.image_id, e
                    )
                )

    def get_clean_image_tasks_for_dependent_images(self) -> List["CleanImageTask"]:
        with self._get_docker_client() as docker_client:
            image_ids = [
                str(possible_child).replace("sha256:", "")
                for possible_child in docker_client.api.images(all=True, quiet=True)
                if self.is_child_image(possible_child, docker_client)
            ]
            return [
                self.create_child_task(CleanImageTask, image_id=image_id)
                for image_id in image_ids
            ]

    def is_child_image(self, possible_child, docker_client) -> bool:
        try:
            inspect = docker_client.api.inspect_image(
                image=str(possible_child).replace("sha256:", "")
            )
            return str(inspect["Parent"]).replace("sha256:", "") == self.image_id
        except Exception:
            return False


class CleanImagesStartingWith(DockerBaseTask):
    starts_with_pattern: str = luigi.Parameter()  # type: ignore

    def register_required(self) -> None:
        with self._get_docker_client() as docker_client:
            image_ids = [
                str(image.id).replace("sha256:", "")
                for image in self.find_images_to_clean(docker_client)
            ]
        self.register_dependencies(
            [
                self.create_child_task(CleanImageTask, image_id=image_id)
                for image_id in image_ids
            ]
        )

    def find_images_to_clean(
        self, docker_client: DockerClient
    ) -> List[docker.models.images.Image]:
        self.logger.info(
            "Going to remove all images starting with %s" % self.starts_with_pattern
        )
        filter_images = find_images_by_tag(
            docker_client, lambda tag: tag.startswith(self.starts_with_pattern)
        )
        for i in filter_images:
            self.logger.info("Going to remove following image: %s" % i.tags)
        return filter_images

    def run_task(self):
        pass


# TODO remove only images that are not represented by current flavor directories
# TODO requires that docker build only returns the image_info without actually building or pulling
class CleanExaslcFlavorImages(FlavorBaseTask):

    def register_required(self):
        flavor_name = self.get_flavor_name()

        if target_docker_repository_config().repository_name == "":
            raise Exception("docker repository name must not be an empty string")

        flavor_name_extension = ":%s" % flavor_name
        starts_with_pattern = (
            target_docker_repository_config().repository_name + flavor_name_extension
        )
        task = self.create_child_task(
            CleanImagesStartingWith, starts_with_pattern=starts_with_pattern
        )
        self.register_dependency(task)

    def run_task(self):
        pass


class CleanExaslcFlavorsImages(FlavorsBaseTask):

    def register_required(self):
        for flavor_path in self.flavor_paths:  # pylint: disable=not-an-iterable
            task = self.create_child_task(
                CleanExaslcFlavorImages, flavor_path=flavor_path
            )
            self.register_dependency(task)

    def run_task(self):
        pass


class CleanExaslcAllImages(DockerBaseTask):

    def register_required(self):
        starts_with_pattern = target_docker_repository_config().repository_name
        task = self.create_child_task(
            CleanImagesStartingWith, starts_with_pattern=starts_with_pattern
        )
        self.register_dependency(task)

    def run_task(self):
        pass
