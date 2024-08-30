from pathlib import PurePosixPath
from typing import List, Tuple, Union
from urllib.parse import parse_qs, urlparse

from exasol_script_languages_container_tool.lib.models.language_activation import (
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
    fragment_path = PurePosixPath(parsed_url.fragment)
    # Cut of leading "/"
    if fragment_path.is_absolute():
        fragment_parts = fragment_path.parts[1:]
    else:
        fragment_parts = fragment_path.parts
    if len(fragment_parts) < 3 or fragment_parts[0] != "buckets":
        raise ValueError(
            f"Invalid URL for language definition '{lang_def}'. Expected format of the fragment in the URL is 'buckets/<bucketfs_name>/<bucket_name>/...'"
        )
    udf_client_bucketfs_name = fragment_parts[1]
    udf_client_bucket_name = fragment_parts[2]
    udf_client_executable = None
    if len(fragment_parts) > 3:
        udf_client_executable = PurePosixPath("/".join(fragment_parts[3:]))

    path = PurePosixPath(parsed_url.path)
    # Cut of leading "/"
    if path.is_absolute():
        path_parts = path.parts[1:]
    else:
        path_parts = path.parts

    if len(fragment_parts) < 2:
        raise ValueError(
            f"Invalid URL for language definition '{lang_def}'. Expected format of the path in the URL is '/<bucketfs_name>/<bucket_name>/...'"
        )
    chroot_bucketfs_name = path_parts[0]
    chroot_bucket_name = path_parts[1]
    chroot_path_in_bucket = None
    if len(path_parts) > 2:
        chroot_path_in_bucket = PurePosixPath("/".join(path_parts[2:]))

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
        chroot_bucketfs_name=chroot_bucketfs_name,
        chroot_bucket_name=chroot_bucket_name,
        chroot_path_in_bucket=chroot_path_in_bucket,
        udf_client_bucketfs_name=udf_client_bucketfs_name,
        udf_client_bucket_name=udf_client_bucket_name,
        udf_client_executable=udf_client_executable,
        parameters=slc_parameters,
        language=slc_language,
    )
