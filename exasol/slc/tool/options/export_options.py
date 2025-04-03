import click

export_options = [
    click.option(
        "--compression/--no-compression",
        default=True,
        help="If set to --compression, a '.tar.gz' file will be created. Otherwise a '.tar' will be created.",
    )
]
