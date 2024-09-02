from pathlib import PurePosixPath

import pytest

from exasol.slc.internal.tasks.upload.language_def_parser import (
    parse_language_definition,
)
from exasol.slc.models.language_definition_components import (
    BuiltInLanguageDefinitionURL,
    ChrootPath,
    LanguageDefinitionURL,
    SLCLanguage,
    SLCParameter,
    UdfClientBucketPath,
    UdfClientRelativePath,
)

CHROOT_PATH_PARAMETERS = [
    (
        "/defaultbfs/default/slc",
        ChrootPath(
            bucketfs_name="defaultbfs",
            bucket_name="default",
            path_in_bucket=PurePosixPath("slc"),
        ),
    ),
    (
        "/defaultbfs/default/",
        ChrootPath(
            bucketfs_name="defaultbfs", bucket_name="default", path_in_bucket=None
        ),
    ),
    (
        "/defaultbfs/default/slc/something",
        ChrootPath(
            bucketfs_name="defaultbfs",
            bucket_name="default",
            path_in_bucket=PurePosixPath("slc/something"),
        ),
    ),
]
UDF_CLIENT_PATH_PARAMETERS = [
    (
        "buckets/defaultbfs/default/slc/exaudf/exaudfclient",
        UdfClientBucketPath(
            bucketfs_name="defaultbfs",
            bucket_name="default",
            executable=PurePosixPath("slc/exaudf/exaudfclient"),
        ),
    ),
    (
        "/buckets/defaultbfs/default/slc/exaudf/exaudfclient",
        UdfClientBucketPath(
            bucketfs_name="defaultbfs",
            bucket_name="default",
            executable=PurePosixPath("slc/exaudf/exaudfclient"),
        ),
    ),
    (
        "exaudf/exaudfclient",
        UdfClientRelativePath(executable=PurePosixPath("exaudf/exaudfclient")),
    ),
    (
        "/exaudf/exaudfclient",
        UdfClientRelativePath(executable=PurePosixPath("/exaudf/exaudfclient")),
    ),
]

PARAMETERS = [
    ("?lang=java", [SLCParameter(key="lang", value=["java"])]),
    ("?lang=python", [SLCParameter(key="lang", value=["python"])]),
    ("?lang=r", [SLCParameter(key="lang", value=["r"])]),
    (
        "?lang=java&my_param=something",
        [
            SLCParameter(key="lang", value=["java"]),
            SLCParameter(key="my_param", value=["something"]),
        ],
    ),
    ("", list()),
]


@pytest.mark.parametrize("chroot_path, expected_chroot_path", CHROOT_PATH_PARAMETERS)
@pytest.mark.parametrize(
    "udf_client_path, expected_udf_client_path", UDF_CLIENT_PATH_PARAMETERS
)
@pytest.mark.parametrize("param, expected_param", PARAMETERS)
def test_lang_def_parser(
    chroot_path,
    expected_chroot_path,
    udf_client_path,
    expected_udf_client_path,
    param,
    expected_param,
):
    if udf_client_path:
        lang_def = (
            f"PYTHON3_TEST=localzmq+protobuf://{chroot_path}{param}#{udf_client_path}"
        )
    else:
        lang_def = f"PYTHON3_TEST=localzmq+protobuf://{chroot_path}{param}"

    alias, result = parse_language_definition(lang_def)
    assert alias == "PYTHON3_TEST"
    assert isinstance(result, LanguageDefinitionURL)
    assert result.chroot_path == expected_chroot_path
    assert result.udf_client_path == expected_udf_client_path
    assert result.parameters == expected_param

    if not udf_client_path.startswith("/buckets"):
        assert f"{alias}={result}" == lang_def


BUILTIN_LANGUAGES = [
    ("builtin_java", BuiltInLanguageDefinitionURL(language=SLCLanguage.Java)),
    ("builtin_python3", BuiltInLanguageDefinitionURL(language=SLCLanguage.Python3)),
    ("builtin_r", BuiltInLanguageDefinitionURL(language=SLCLanguage.R)),
]


@pytest.mark.parametrize("builtin_str, expected", BUILTIN_LANGUAGES)
def test_lang_def_parser_builtin(
    builtin_str,
    expected,
):
    lang_def = f"PYTHON3_TEST={builtin_str}"
    alias, result = parse_language_definition(lang_def)
    assert alias == "PYTHON3_TEST"
    assert isinstance(result, BuiltInLanguageDefinitionURL)
    assert result == expected

    assert f"{alias}={result}" == lang_def


def test_lang_def_parser_invalid_builtin():
    lang_def = f"PYTHON3_TEST=builtin_rust"
    with pytest.raises(ValueError):
        _, _ = parse_language_definition(lang_def)


def test_lang_def_parser_invalid_chroot():
    lang_def = f"PYTHON3_TEST=localzmq+protobuf:///home/#buckets/bfsdefault/default/exaudf/exaudfclient"
    with pytest.raises(ValueError):
        _, _ = parse_language_definition(lang_def)


INVALID_UDF_PATHS = [
    "buckets/exaudfclient",
    "/buckets/exaudfclient",
    "/buckets/",
    "buckets/",
]


@pytest.mark.parametrize("invalid_udf_client_path", INVALID_UDF_PATHS)
def test_lang_def_parser_invalid_udf_path(invalid_udf_client_path):
    lang_def = f"PYTHON3_TEST=localzmq+protobuf:///bfsdefault/default/slc#{invalid_udf_client_path}"
    with pytest.raises(ValueError):
        _, _ = parse_language_definition(lang_def)
