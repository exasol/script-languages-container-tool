import textwrap


def _execute_script(connection, language, script_name, script_body):
    script_body = textwrap.dedent(script_body).strip()
    connection.execute(
        f"CREATE OR REPLACE {language} SCALAR SCRIPT {script_name}(i INT)\n"
        f"RETURNS INT AS\n{script_body}\n/"
    )
    result = connection.execute(f"SELECT {script_name}(0)").fetchone()
    assert result == (0,)


def test_python3(pyexasol_connection, activate_script_languages_for_function):
    try:
        _execute_script(
            pyexasol_connection,
            "PYTHON3",
            "test_python3",
            """
            def run(ctx):
                return 0
            """,
        )
    finally:
        pyexasol_connection.execute("DROP SCRIPT test_python3")


def test_java(pyexasol_connection, activate_script_languages_for_function):
    try:
        _execute_script(
            pyexasol_connection,
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
        pyexasol_connection.execute("DROP SCRIPT test_java")


def test_r(pyexasol_connection, activate_script_languages_for_function):
    try:
        _execute_script(
            pyexasol_connection,
            "R",
            "test_r",
            """
            run <- function(ctx) {
                return(0)
            }
            """,
        )
    finally:
        pyexasol_connection.execute("DROP SCRIPT test_r")
