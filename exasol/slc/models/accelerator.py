from enum import Enum


class Accelerator(Enum):
    """
    This enum serves as a definition of values for possible accelerators for `run-db-tests.
    """

    NONE = "none"
    NVIDA = "nvidia"


def defaultAccelerator() -> Accelerator:
    return Accelerator.NONE
