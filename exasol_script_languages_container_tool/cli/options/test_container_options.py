import click

test_container_options = [
    click.option('--test-container-folder', type=click.Path(exists=True, file_okay=False, dir_okay=True),
                 default="./test_container",
                 help="Test folder containing 'Dockerfile', tests and test-data.")
]
