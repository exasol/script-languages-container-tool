from pathlib import PurePosixPath
from typing import List, Tuple, Union
from urllib.parse import parse_qs, urlparse

from exasol_script_languages_container_tool.lib.models.language_activation import (
    BuiltInLanguageDefinitionURL,
    ChrootPath,
    LanguageDefinitionURL,
    SLCLanguage,
    SLCParameter,
    UdfClientAbsolutePath,
    UdfClientRelativePath,
)


def _parse_builtin_language_definition(url: str) -> BuiltInLanguageDefinitionURL:
    language = url.replace("builtin_", "")
    try:
        slc_language = next(
            slc_language_enum
            for slc_language_enum in SLCLanguage
            if slc_language_enum.name.lower() == language.lower()
        )
    except StopIteration:
        raise ValueError(f"Unknown builtin language: {url}")
    return BuiltInLanguageDefinitionURL(language=slc_language)


def _build_udf_client_abs_path_from_fragments(
    fragment_parts: Tuple[str, ...]
) -> UdfClientAbsolutePath:
    if len(fragment_parts) < 3 or fragment_parts[0] != "buckets":
        raise ValueError(
            f"Expected format of the fragment in the URL for absolute udf client path is "
            f"'/buckets/<bucketfs_name>/<bucket_name>/...' or"
            f"'buckets/<bucketfs_name>/<bucket_name>/...' or"
        )
    udf_client_executable = None
    if len(fragment_parts) > 3:
        udf_client_executable = PurePosixPath("/".join(fragment_parts[3:]))

    return UdfClientAbsolutePath(
        bucketfs_name=fragment_parts[1],
        bucket_name=fragment_parts[2],
        executable=udf_client_executable,
    )


def _parse_udf_client_path(
    fragment: str,
) -> Union[UdfClientRelativePath, UdfClientAbsolutePath]:
    fragment_path = PurePosixPath(fragment)
    fragment_parts = fragment_path.parts

    if len(fragment_parts) == 0:
        return UdfClientRelativePath(executable=None)

    if fragment_path.is_absolute():
        fragment_parts = fragment_path.parts[1:]  # Remove leading "/"
        return _build_udf_client_abs_path_from_fragments(fragment_parts)
    elif fragment_parts[0] == "buckets":
        return _build_udf_client_abs_path_from_fragments(fragment_parts)
    else:
        udf_client_path = UdfClientRelativePath(
            executable=PurePosixPath("/".join(fragment_parts))
        )
    return udf_client_path


def _parse_chroot_path(
    p: str,
) -> ChrootPath:
    path = PurePosixPath(p)

    # Cut of leading "/"
    if path.is_absolute():
        path_parts = path.parts[1:]
    else:
        path_parts = path.parts

    if len(path_parts) < 2:
        raise ValueError(
            f"Expected format of the URL path is "
            f"'/<bucketfs_name>/<bucket_name>/...' or"
            f"'<bucketfs_name>/<bucket_name>/...' or"
        )
    chroot_bucketfs_name = path_parts[0]
    chroot_bucket_name = path_parts[1]
    chroot_path_in_bucket = None
    if len(path_parts) > 2:
        chroot_path_in_bucket = PurePosixPath("/".join(path_parts[2:]))
    return ChrootPath(
        bucketfs_name=chroot_bucketfs_name,
        bucket_name=chroot_bucket_name,
        path_in_bucket=chroot_path_in_bucket,
    )


def parse_language_definition(
    lang_def: str,
) -> Tuple[str, Union[LanguageDefinitionURL, BuiltInLanguageDefinitionURL]]:
    alias_end = lang_def.find("=")
    alias = lang_def[0:alias_end]
    url = lang_def[alias_end + 1 :]
    if url.startswith("builtin_"):
        return alias, _parse_builtin_language_definition(url)
    parsed_url = urlparse(url)
    if parsed_url.hostname:
        raise ValueError(f"Invalid language definition: '{lang_def}'")
    slc_parameters = [
        SLCParameter(key, value) for key, value in parse_qs(parsed_url.query).items()
    ]
    try:
        udf_client_path = _parse_udf_client_path(parsed_url.fragment)
        chroot_path = _parse_chroot_path(parsed_url.path)
    except ValueError as e:
        raise ValueError(f"Invalid language definition: '{lang_def}'") from e

    return alias, LanguageDefinitionURL(
        protocol=parsed_url.scheme,
        parameters=slc_parameters,
        chroot_path=chroot_path,
        udf_client_path=udf_client_path,
    )
