import click

TEST_CONTAINER_DEFAULT_DIRECTORY = "./test_container"

test_container_options = [
    click.option(
        "--test-container-folder",
        type=click.Path(exists=True, file_okay=False, dir_okay=True),
        default=TEST_CONTAINER_DEFAULT_DIRECTORY,
        help="Test folder containing 'Dockerfile', tests and test-data.",
    )
]
