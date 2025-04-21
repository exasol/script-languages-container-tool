#!/usr/bin/env python3
from exasol_python_test_framework import docker_db_environment, udf


class TestGPUDisabled(udf.TestCase):

    def test_gpu_disabled(self):
        select_sql = """
            SELECT PARAM_VALUE FROM EXA_METADATA
            WHERE PARAM_NAME LIKE '%accelerator%'
            ORDER BY PARAM_NAME;
        """
        rows = self.query(select_sql)
        self.assertRowsEqual([("0",), ("0",)], rows)


if __name__ == "__main__":
    udf.main()
