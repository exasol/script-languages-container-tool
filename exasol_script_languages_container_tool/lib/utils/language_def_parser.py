from typing import List, Tuple, Union
from urllib.parse import urlparse

from exasol_script_languages_container_tool.lib.api.get_language_activation_builder import (
    BuiltInLanguageDefinitionURL,
    LanguageDefinitionURL,
    SLCLanguage,
)
from exasol_script_languages_container_tool.lib.api.language_activation import (
    SLCParameter,
)


def parse_language_definition(
    lang_def: str,
) -> Tuple[str, Union[LanguageDefinitionURL, BuiltInLanguageDefinitionURL]]:
    alias_end = lang_def.find("=")
    alias = lang_def[0:alias_end]
    url = lang_def[alias_end + 1 :]
    if url.startswith("builtin"):
        lang = url.replace("builtin_", "")
        for slc_builtin_language in SLCLanguage:
            if slc_builtin_language.name.lower() == lang.lower():
                return alias, BuiltInLanguageDefinitionURL(
                    language=slc_builtin_language
                )
        raise ValueError(f"Unknown builtin language: {url}")
    parsed_url = urlparse(url)
    parameters = parsed_url.query.split("&")
    language = ""
    slc_parameters: List[SLCParameter] = list()
    for param in parameters:
        key, value = param.split("=")
        if key == "lang":
            language = value
        else:
            slc_parameters.append(SLCParameter(key=key, value=value))
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
