import subprocess
import unittest


class ConsoleScriptTest(unittest.TestCase):

    def test_console_script(self):
        return_code = subprocess.call("poetry install", shell=True)
        self.assertEqual(0, return_code, "Poetry install failed")
        return_code = subprocess.call("poetry run exaslct --help", shell=True)
        self.assertEqual(0, return_code)
