import click


@click.group()
def cli():
    """
    EXASLCT - Exasol Script Languages Container Tool

    Build, deploy, push and test Exasol Script-Languages-Container

    Examples:

        Print this help message:

            $ exaslct --help

        Build a script-languages-container:

            $ exaslct build --flavor-path ./flavors/my_flavor
    """
    pass
