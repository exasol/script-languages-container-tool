import unittest
from typing import List, Any, Tuple

import click.types

from exasol_script_languages_container_tool.cli import commands
from exasol_script_languages_container_tool.lib import api
import inspect

import utils as exaslct_utils


def is_click_command(obj: Any) -> bool:
    return isinstance(obj, click.Command)


class ClickApiConsistency(unittest.TestCase):

    @staticmethod
    def _replace_list_with_tuple(x: Any):
        """
        Click stores default values as list if 'Multiple'=true. However, for plain Python methods we
        need to use (immutable) tuples for declaring default value. Hence, we need to convert lists with tuples
        for comparison.
        """
        if type(x) == list:
            return tuple(x)
        else:
            return x

    def _defaults_of_click_call(self, click_call: click.Command) -> List[Tuple[str, Any]]:
        return [(o.name, self._replace_list_with_tuple(o.default)) for o in click_call.params if not o.required]

    @staticmethod
    def _param_names_of_click_call(click_call: click.Command) -> List[str]:
        return [o.name for o in click_call.params]

    def test_api_arguments(self):
        """
        Validate that the argument lists for all commands match!
        """

        # Get all click commands in module exasol_script_languages_container_tool.cli.commands
        click_commands = [c[1] for c in inspect.getmembers(commands, is_click_command)]
        # Get all functions in module exasol_script_languages_container_tool.lib.api
        api_functions = [f[1] for f in inspect.getmembers(api, inspect.isfunction)]

        # Now iterate over the list and compare consistency
        for cli_call, api_call in zip(click_commands, api_functions):
            cli_spec = inspect.getfullargspec(cli_call.callback)
            api_spec = inspect.getfullargspec(api_call)

            exaslct_utils.multiassert([lambda: self.assertEqual(api_spec.args, cli_spec.args),
                                       lambda: self.assertEqual(api_spec.annotations, cli_spec.annotations),
                                       lambda: self.assertEqual(api_spec.args,
                                                                self._param_names_of_click_call(cli_call))], self)

    def test_api_default_values(self):
        """
        Validate that the default values for all commands match!
        """

        # Get all click commands in module exasol_script_languages_container_tool.cli.commands
        click_commands = [c[1] for c in inspect.getmembers(commands, is_click_command)]
        # Get all functions in module exasol_script_languages_container_tool.lib.api
        api_functions = [f[1] for f in inspect.getmembers(api, inspect.isfunction)]

        # Now iterate over the list and compare consistency
        for cli_call, api_call in zip(click_commands, api_functions):
            api_spec = inspect.getfullargspec(api_call)
            cli_defaults = self._defaults_of_click_call(cli_call)

            self.assertEqual(len(cli_defaults), len(api_spec.defaults))
            for api_default_value, cli_default in zip(api_spec.defaults, cli_defaults):
                cli_param_name, cli_default_value = cli_default
                if api_default_value != cli_default_value:
                    self.fail(f"Default value for parameter '{cli_param_name}' "
                              f"for method '{api_call.__name__}' does not match. "
                              f"API method has default value '{api_default_value}' "
                              f"while CLI method has default value '{cli_default_value}'")

    def test_same_functions(self):
        """
        Validate that Click commands and API functions match!
        For that we use inspect to get all classes of type click.Command in module 'commands',
        and on the other hand get all functions in module 'api'. The list of names from both most be identical.
        """
        click_commands = inspect.getmembers(commands, is_click_command)
        click_command_names = [c[0] for c in click_commands]
        api_functions = inspect.getmembers(api, inspect.isfunction)
        api_function_names = [a[0] for a in api_functions]
        self.assertEqual(click_command_names, api_function_names)


if __name__ == '__main__':
    unittest.main()
