from enum import Enum


class CompressionStrategy(Enum):
    """
    This enum serves as a definition of values for possible compression strategy of the script-lamnguages-container file.
    """

    NONE = "none"
    GZIP = "gzip"


def defaultCompressionStrategy() -> CompressionStrategy:
    return CompressionStrategy.GZIP
