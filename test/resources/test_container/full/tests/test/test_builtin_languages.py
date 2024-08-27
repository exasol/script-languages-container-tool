#!/usr/bin/env python3

from exasol_python_test_framework import udf


class DockerDBEnvironmentTest(udf.TestCase):

    def test_python3(self):
        schema = "DockerDBEnvironmentTest"
        try:
            self.query(
                udf.fixindent("DROP SCHEMA %s CASCADE" % schema), ignore_errors=True
            )
            self.query(udf.fixindent("CREATE SCHEMA %s" % schema))
            self.query(udf.fixindent("OPEN SCHEMA %s" % schema))
            self.query(
                udf.fixindent(
                    """
                CREATE OR REPLACE PYTHON3 SCALAR SCRIPT test_python3(i int) returns int AS

                def run(ctx):
                  return 0
                /
                """
                )
            )
            self.query("select test_python3(0)")
        finally:
            self.query(udf.fixindent("DROP SCHEMA %s CASCADE" % schema))

    def test_java(self):
        schema = "DockerDBEnvironmentTest"
        try:
            self.query(
                udf.fixindent("DROP SCHEMA %s CASCADE" % schema), ignore_errors=True
            )
            self.query(udf.fixindent("CREATE SCHEMA %s" % schema))
            self.query(udf.fixindent("OPEN SCHEMA %s" % schema))
            self.query(
                udf.fixindent(
                    """
                CREATE OR REPLACE JAVA SCALAR SCRIPT test_java(i int) returns int AS

                    class TEST_JAVA {
                        static Integer run(ExaMetadata exa, ExaIterator ctx) throws Exception {
                            return 0;
                        }
                    }
                /
                """
                )
            )
            self.query("select test_java(0)")
        finally:
            self.query(udf.fixindent("DROP SCHEMA %s CASCADE" % schema))

    def test_r(self):
        schema = "DockerDBEnvironmentTest"
        try:
            self.query(
                udf.fixindent("DROP SCHEMA %s CASCADE" % schema), ignore_errors=True
            )
            self.query(udf.fixindent("CREATE SCHEMA %s" % schema))
            self.query(udf.fixindent("OPEN SCHEMA %s" % schema))
            self.query(
                udf.fixindent(
                    """
                CREATE OR REPLACE R SCALAR SCRIPT test_r(i int) returns int AS

                    run <- function(ctx) {
                        return(0);
                    }
                /
                """
                )
            )
            self.query("select test_r(0)")
        finally:
            self.query(udf.fixindent("DROP SCHEMA %s CASCADE" % schema))


if __name__ == "__main__":
    udf.main()
