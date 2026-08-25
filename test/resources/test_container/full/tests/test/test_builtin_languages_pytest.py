import pyexasol


def _execute_script(connection, language, script_name, script_body):
    connection.execute(
        f"""
        CREATE OR REPLACE {language} SCALAR SCRIPT {script_name}(i INT)
        RETURNS INT AS
        {script_body}
        /
        """
    )
    result = connection.execute(f"SELECT {script_name}(0)").fetchone()
    assert result == (0,)


def test_python3(backend_aware_database_params, activate_script_languages_for_function):
    with pyexasol.connect(**backend_aware_database_params) as connection:
        try:
            _execute_script(
                connection,
                "PYTHON3",
                "test_python3",
                """
                def run(ctx):
                    return 0
                """,
            )
        finally:
            connection.execute("DROP SCRIPT test_python3")


def test_java(backend_aware_database_params, activate_script_languages_for_function):
    with pyexasol.connect(**backend_aware_database_params) as connection:
        try:
            _execute_script(
                connection,
                "JAVA",
                "test_java",
                """
                class TEST_JAVA {
                    static Integer run(ExaMetadata exa, ExaIterator ctx) {
                        return 0;
                    }
                }
                """,
            )
        finally:
            connection.execute("DROP SCRIPT test_java")


def test_r(backend_aware_database_params, activate_script_languages_for_function):
    with pyexasol.connect(**backend_aware_database_params) as connection:
        try:
            _execute_script(
                connection,
                "R",
                "test_r",
                """
                run <- function(ctx) {
                    return(0)
                }
                """,
            )
        finally:
            connection.execute("DROP SCRIPT test_r")
