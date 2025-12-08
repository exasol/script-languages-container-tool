import click
from exasol_integration_test_docker_environment.cli.options.test_environment_options import (
    LATEST_DB_VERSION,
)
from exasol_integration_test_docker_environment.lib.test_environment.parameter.docker_db_test_environment_parameter import (
    DbOsAccess,
)

docker_db_options = [
    click.option(
        "--docker-db-image-version",
        type=str,
        default=LATEST_DB_VERSION,
        show_default=True,
        help="""Docker DB Image Version against which the tests should run.""",
    ),
    click.option(
        "--docker-db-image-name",
        type=str,
        default="""exasol/docker-db""",
        show_default=True,
        help="""Docker DB Image Name against which the tests should run.""",
    ),
    click.option(
        "--db-os-access",
        type=click.Choice([e.name for e in DbOsAccess]),
        metavar="METHOD",
        default="""DOCKER_EXEC""",
        show_default=True,
        help="""How to access file system and command line of the
     		 database operating system. Experimental option, will show no
     		 effect until implementation of feature SSH access is
     		 completed.""",
    ),
    click.option(
        "--create-certificates/--no-create-certificates",
        default=False,
        help="""Creates and injects SSL certificates to the Docker DB container.""",
    ),
    click.option(
        "--additional-db-parameter",
        "-p",
        type=str,
        multiple=True,
        default=(),
        help="""Additional database parameter which will be injected to EXAConf. Value should have format '-param=value'.""",
    ),
    click.option(
        "--docker-environment-variable",
        type=str,
        multiple=True,
        default=[],
        help="""An environment variable which will be added to the docker-db.
                The variable needs to have format "key=value".
                For example "HTTPS_PROXY=192.168.1.5".
                You can repeat this option to add further environment variables.""",
    ),
]
