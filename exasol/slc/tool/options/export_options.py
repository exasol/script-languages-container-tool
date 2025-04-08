import click

from exasol.slc.models.compression_strategy import (
    CompressionStrategy,
    defaultCompressionStrategy,
)

export_options = [
    click.option(
        "--compression-strategy",
        default=defaultCompressionStrategy().value,
        type=click.Choice([v.value for v in CompressionStrategy]),
        show_default=True,
        help=f"Compression strategy to be applied to compress the exported container file."
        f" Possible values are {[v.value for v in CompressionStrategy]}",
    )
]
