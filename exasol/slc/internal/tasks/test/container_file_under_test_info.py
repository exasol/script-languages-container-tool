from dataclasses import dataclass


@dataclass
class ContainerFileUnderTestInfo:
    target_name: str
    container_file: str
    is_new: bool
