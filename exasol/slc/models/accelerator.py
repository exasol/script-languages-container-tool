from enum import Enum
from typing import List


class Accelerator(Enum):
    """
    This enum serves as a definition of values for possible accelerators for `run-db-tests`.
    """

    NONE = "none"
    NVIDA = "nvidia"


def defaultAccelerator() -> Accelerator:
    return Accelerator.NONE


def acceleratorValues() -> list[str]:
    return [a.value for a in Accelerator]
