from typing import Tuple, Any

import click


def handle_invalid_argument_error(error: Tuple[Any, ...]):
    for e in error:
        print(error)
    ctx = click.get_current_context()
    click.echo(ctx.get_help())
    exit(1)
