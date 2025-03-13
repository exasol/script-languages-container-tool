import textwrap
from pathlib import Path
from typing import Tuple

from exasol_integration_test_docker_environment.lib.utils.api_function_decorators import (
    cli_function,
)

from exasol.slc.internal.tasks.upload.language_definition import LanguageDefinition


@cli_function
def generate_language_activation(
    flavor_path: str,
    bucketfs_name: str,
    bucket_name: str,
    container_name: str,
    path_in_bucket: str = "",
) -> Tuple[str, str, str]:
    """
    Generate the language activation statement.
    :return: A tuple of language definition statements: The first one is the alter session statement,
             the second one the alter system statement; the last string contains a summary which is useful to print to
             the user.
    """

    language_definition = LanguageDefinition(
        release_name=container_name,
        flavor_path=flavor_path,
        bucketfs_name=bucketfs_name,
        bucket_name=bucket_name,
        path_in_bucket=path_in_bucket,
    )

    command_line_output_str = textwrap.dedent(
        f"""

            In SQL, you can activate the languages supported by the {Path(flavor_path).name}
            flavor by using the following statements:


            To activate the flavor only for the current session:

            {language_definition.generate_alter_session()}


            To activate the flavor on the system:

            {language_definition.generate_alter_system()}
            """
    )
    return (
        language_definition.generate_alter_session(),
        language_definition.generate_alter_system(),
        command_line_output_str,
    )
