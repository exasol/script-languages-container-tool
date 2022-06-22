import textwrap
from pathlib import Path

from exasol_script_languages_container_tool.lib.tasks.upload.language_definition import LanguageDefinition


def generate_language_activation(
        flavor_path: str,
        bucketfs_name: str,
        bucket_name: str,
        container_name: str,
        path_in_bucket: str = ''):
    """
    Generate the language activation statement.
    """

    language_definition = \
        LanguageDefinition(release_name=container_name,
                           flavor_path=flavor_path,
                           bucketfs_name=bucketfs_name,
                           bucket_name=bucket_name,
                           path_in_bucket=path_in_bucket)

    command_line_output_str = textwrap.dedent(f"""

            In SQL, you can activate the languages supported by the {Path(flavor_path).name}
            flavor by using the following statements:


            To activate the flavor only for the current session:

            {language_definition.generate_alter_session()}


            To activate the flavor on the system:

            {language_definition.generate_alter_system()}
            """)
    print(command_line_output_str)
