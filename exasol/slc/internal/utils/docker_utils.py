from typing import Callable, Dict, List, TextIO

import docker.models.containers
import docker.models.images
from docker import DockerClient


def find_images_by_tag(
    client: DockerClient, condition: Callable[[str], bool]
) -> List[docker.models.images.Image]:
    images = client.images.list()
    filter_images = [
        image
        for image in images
        if image.tags is not None
        and len(image.tags) > 0
        and any([condition(tag) for tag in image.tags])
    ]
    return filter_images


def exec_run_and_write_to_stream(
    client: docker.client,
    container: docker.models.containers.Container,
    cmd: str,
    output_io: TextIO,
    environment: Dict,
) -> int:
    _id = client.api.exec_create(
        container=container.id, cmd=cmd, environment=environment
    )
    output_stream = client.api.exec_start(_id, detach=False, stream=True)
    for output_chunk in output_stream:
        output_io.write(output_chunk.decode("utf-8"))
    ret = client.api.exec_inspect(_id)
    return ret["ExitCode"]
