from pathlib import PurePosixPath
from typing import Tuple, Union
from urllib.parse import parse_qs, urlparse

from exasol.slc.models.language_definition_components import (
    BuiltInLanguageDefinitionURL,
    ChrootPath,
    LanguageDefinitionURL,
    SLCLanguage,
    SLCParameter,
    UdfClientBucketPath,
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
    fragment_parts: tuple[str, ...],
) -> UdfClientBucketPath:
    if len(fragment_parts) < 4:
        raise ValueError(
            f"Expected format of the fragment in the URL for a bucket udf client path is "
            f"'/buckets/<bucketfs_name>/<bucket_name>/<executable>' or"
            f" 'buckets/<bucketfs_name>/<bucket_name>/<executable>'"
        )

    udf_client_executable = PurePosixPath("/".join(fragment_parts[3:]))
    return UdfClientBucketPath(
        bucketfs_name=fragment_parts[1],
        bucket_name=fragment_parts[2],
        executable=udf_client_executable,
    )


def _parse_udf_client_path(
    fragment: str,
) -> Union[UdfClientRelativePath, UdfClientBucketPath]:
    fragment_path = PurePosixPath(fragment)
    fragment_parts = fragment_path.parts

    if len(fragment_parts) == 0 or (
        fragment_path.is_absolute() and len(fragment_parts) == 1
    ):
        raise ValueError("Udf client executable path must not be empty.")

    if fragment_path.is_absolute():
        fragment_parts = fragment_path.parts[1:]  # Remove leading "/"

    if fragment_parts[0] == "buckets":
        return _build_udf_client_abs_path_from_fragments(fragment_parts)
    else:
        # Use original path from URL as is
        udf_client_path = UdfClientRelativePath(executable=fragment_path)
    return udf_client_path


def _parse_chroot_path(
    p: str,
) -> ChrootPath:
    path = PurePosixPath(p)

    if not path.is_absolute() or len(path.parts) < 3:
        raise ValueError(
            f"Expected format of the URL path is "
            f"'/<bucketfs_name>/<bucket_name>/...'"
        )
    path_parts = path.parts[1:]
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
) -> tuple[str, Union[LanguageDefinitionURL, BuiltInLanguageDefinitionURL]]:
    alias_end = lang_def.find("=")
    alias = lang_def[0:alias_end]
    url = lang_def[alias_end + 1 :]
    if url.startswith("builtin_"):
        return alias, _parse_builtin_language_definition(url)
    parsed_url = urlparse(url)
    if parsed_url.hostname:
        raise ValueError(f"Invalid language definition: '{lang_def}'")
    slc_parameters = [
        SLCParameter(key=key, value=v)
        for key, value in parse_qs(parsed_url.query).items()
        for v in value
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
