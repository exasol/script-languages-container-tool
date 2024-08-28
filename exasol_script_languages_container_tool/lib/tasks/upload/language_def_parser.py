from typing import List, Tuple, Union
from urllib.parse import parse_qs, urlparse

from exasol_script_languages_container_tool.lib.tasks.upload.language_activation import (
    BuiltInLanguageDefinitionURL,
    LanguageDefinitionURL,
    SLCLanguage,
    SLCParameter,
)


def _parse_builtin_language_definition(url: str) -> BuiltInLanguageDefinitionURL:
    lang = url.replace("builtin_", "")
    for slc_builtin_language in SLCLanguage:
        if slc_builtin_language.name.lower() == lang.lower():
            return BuiltInLanguageDefinitionURL(language=slc_builtin_language)
    raise ValueError(f"Unknown builtin language: {url}")


def _parse_parameters(query_string: str) -> Tuple[str, List[SLCParameter]]:
    values = parse_qs(query_string)
    language_list = values["lang"]
    if len(language_list) != 1:
        raise ValueError(
            f"Unexpected number of languages in URL. query_string: '{query_string}'"
        )
    slc_parameters: List[SLCParameter] = [
        SLCParameter(key, value) for key, value in values.items() if key != "lang"
    ]
    return language_list[0], slc_parameters


def parse_language_definition(
    lang_def: str,
) -> Tuple[str, Union[LanguageDefinitionURL, BuiltInLanguageDefinitionURL]]:
    alias_end = lang_def.find("=")
    alias = lang_def[0:alias_end]
    url = lang_def[alias_end + 1 :]
    if url.startswith("builtin_"):
        return alias, _parse_builtin_language_definition(url)
    parsed_url = urlparse(url)
    language, slc_parameters = _parse_parameters(parsed_url.query)

    # fragment is supposed to be something like:
    # 'buckets/exaudf/exaudfclient_py3'
    # We remove the given bucket prefix 'buckets/'
    udf_client_path_within_container = parsed_url.fragment.replace("buckets///", "")
    if not udf_client_path_within_container:
        raise ValueError(
            f"URL {url} for alias '{alias}' is not in expected format: Path to udf client is empty."
        )

    slc_language = None
    for slc_language_enum in SLCLanguage:
        if slc_language_enum.value.lower() == language.lower():
            slc_language = slc_language_enum
            break
    if slc_language is None:
        raise ValueError(
            f"Unknown language in language definition for alias '{alias}' and url '{url}'"
        )

    return alias, LanguageDefinitionURL(
        protocol=parsed_url.scheme,
        bucketfs_name="",
        bucket_name="",
        path_in_bucket="",
        container_name="",
        udf_client_path_within_container=udf_client_path_within_container,
        parameters=slc_parameters,
        language=slc_language,
    )