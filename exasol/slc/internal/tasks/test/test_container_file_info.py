from dataclasses import dataclass


@dataclass
class TestContainerFileInfo:
    target_name: str
    container_file: str
    is_new: bool
