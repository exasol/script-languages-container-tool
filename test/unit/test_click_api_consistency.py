import inspect
import json
from pathlib import Path

import pytest
from exasol_integration_test_docker_environment.testing.api_consistency_utils import (  # type: ignore
    defaults_of_click_call,
    get_click_and_api_function_names,
    get_click_and_api_functions,
    param_names_of_click_call,
)

from exasol.slc import api
from exasol.slc.internal.tasks.test.test_runner_db_test_base_task import (
    get_generic_language_tests,
    get_test_folders,
    read_ci_json,
)
from exasol.slc.tool import commands

IGNORE_LIST = ["compression_strategy", "accelerator"]


def test_api_arguments():
    """
    Validate that the argument lists for all commands match!
    """

    click_commands, api_functions = get_click_and_api_functions(commands, api)
    # Now iterate over the list and compare consistency
    for cli_call, api_call in zip(click_commands, api_functions):
        cli_spec = inspect.getfullargspec(cli_call.callback)
        api_spec = inspect.getfullargspec(api_call)

        # We don't compare the annotation for the return type as this is allowed to be different between CLI and API
        if "return" in api_spec.annotations:
            del api_spec.annotations["return"]

            for annotation_to_ignore in IGNORE_LIST:
                if (
                    annotation_to_ignore in api_spec.annotations
                    and annotation_to_ignore in cli_spec.annotations
                ):
                    del api_spec.annotations[annotation_to_ignore]
                    del cli_spec.annotations[annotation_to_ignore]

            assert api_spec.args == cli_spec.args
            assert api_spec.annotations == cli_spec.annotations
            assert api_spec.args == param_names_of_click_call(cli_call)


def test_api_default_values():
    """
    Validate that the default values for all commands match!
    """

    click_commands, api_functions = get_click_and_api_functions(commands, api)

    # Now iterate over the list and compare consistency
    for cli_call, api_call in zip(click_commands, api_functions):
        api_spec_defaults = inspect.getfullargspec(api_call).defaults or tuple()
        cli_defaults = defaults_of_click_call(cli_call)

        assert len(cli_defaults) == len(
            api_spec_defaults
        ), f"{cli_call},{cli_defaults},{api_spec_defaults}"

        for api_default_value, cli_default in zip(api_spec_defaults, cli_defaults):
            cli_param_name, cli_default_value = cli_default
            if (
                api_default_value != cli_default_value
                and cli_param_name not in IGNORE_LIST
            ):
                pytest.fail(
                    f"Default value for parameter '{cli_param_name}' "
                    f"for method '{api_call.__name__}' does not match. "
                    f"API method has default value '{api_default_value}' "
                    f"while CLI method has default value '{cli_default_value}'"
                )


def test_same_functions():
    """
    Validate that Click commands and API functions match!
    For that we use inspect to get all classes of type click.Command in module 'commands',
    and on the other hand get all functions in module 'api'. The list of names from both most be identical.
    """
    click_command_names, api_function_names = get_click_and_api_function_names(
        commands, api
    )

    assert click_command_names == api_function_names


def _get_ci_json_data():
    ci_json_data = {
        "test_config": {
            "test_sets": [
                {"generic_language_tests": ["g00", "g01"], "folders": ["f00", "f01"]},
                {"generic_language_tests": ["g10", "g11"], "folders": ["f10", "f11"]},
                {"generic_language_tests": ["g20", "g21"], "folders": ["f20", "f21"]},
            ]
        }
    }
    return ci_json_data


def _get_ci_json_folders():
    ci_json_files = "f00 f01 f10 f11 f20 f21"
    return ci_json_files


def _get_ci_json_lang_tests():
    ci_json_lang_tests = "g00 g01 g10 g11 g20 g21"
    return ci_json_lang_tests


def _get_ci_json_file_lang_tests():
    ci_json_files = _get_ci_json_folders()
    ci_json_lang_tests = _get_ci_json_lang_tests()
    files_and_lang_tests = {
        "generic_language_tests": ci_json_lang_tests,
        "test_folders": ci_json_files,
    }
    return files_and_lang_tests


def _created_ci_json_file(tmp_path: Path):
    ci_json_data = _get_ci_json_data()
    json_file_path = tmp_path / "temp_data.json"
    with open(json_file_path, "w") as json_file:
        json.dump(ci_json_data, json_file)
    return json_file_path


def test_get_generic_language_tests(tmp_path: Path):
    json_file_path = _created_ci_json_file(tmp_path)
    ci_json_dict = read_ci_json(json_file_path)
    actual_res = get_generic_language_tests(ci_json_dict)
    expected_res = _get_ci_json_lang_tests().split()
    assert actual_res == expected_res


def test_get_test_folders(tmp_path: Path):
    json_file_path = _created_ci_json_file(tmp_path)
    ci_json_dict = read_ci_json(json_file_path)
    actual_res = get_test_folders(ci_json_dict)
    expected_res = _get_ci_json_folders().split()
    assert actual_res == expected_res


def test_parse_ci_json(tmp_path: Path):
    json_file_path = _created_ci_json_file(tmp_path)
    actual_res = read_ci_json(json_file_path)
    expected_res = _get_ci_json_file_lang_tests()
    assert actual_res == expected_res
