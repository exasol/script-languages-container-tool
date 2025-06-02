from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import List, Optional, Union
from urllib.parse import ParseResult, urlencode, urlunparse

from exasol.slc.models.language_definition_common import (
    SLCLanguage,
    SLCParameter,
    UdfClientRelativePath,
)


@dataclass
class UdfClientBucketPath:
    """
    Path to the udf client relative to a BucketFS path. For example `buckets/bfsdefault/default/exaudf/exaudfclient_py3`
    """

    bucketfs_name: str
    bucket_name: str
    executable: PurePosixPath

    def __str__(self) -> str:
        return f"buckets/{self.bucketfs_name}/{self.bucket_name}/" f"{self.executable}"


@dataclass
class ChrootPath:
    """
    Path to the Script Languages Container root directory in the BucketFS. For example: `/bfsdefault/default/my_slc`
    """

    bucketfs_name: str
    bucket_name: str
    path_in_bucket: Optional[PurePosixPath] = None

    def __str__(self) -> str:
        return f"/{self.bucketfs_name}/{self.bucket_name}/{self.path_in_bucket or ''}"


@dataclass
class LanguageDefinitionURL:
    """
    Contains all necessary components of the Language Definition URL.
    """

    protocol: str
    parameters: list[SLCParameter]
    chroot_path: ChrootPath
    udf_client_path: Union[UdfClientBucketPath, UdfClientRelativePath]

    def __str__(self) -> str:
        query_params = [(p.key, p.value) for p in self.parameters]
        query_string = urlencode(query_params)
        url = urlunparse(
            ParseResult(
                scheme=self.protocol,
                netloc=f"/{self.chroot_path.bucketfs_name}",
                path=f"/{self.chroot_path.bucket_name}/{self.chroot_path.path_in_bucket or ''}",
                params="",
                query=query_string,
                fragment=str(self.udf_client_path),
            )
        )
        return url


@dataclass
class BuiltInLanguageDefinitionURL:
    """
    Contains the language of the Builtin Language Definition.
    """

    language: SLCLanguage

    def __str__(self) -> str:
        return f"builtin_{self.language.name.lower()}"


@dataclass
class LanguageDefinitionComponents:
    """
    Contains the alias and the Language Definition URL if custom Script Languages Container or BuiltIn Language
    Definition if BuiltIn language.
    """

    alias: str
    url: Union[LanguageDefinitionURL, BuiltInLanguageDefinitionURL]

    @property
    def is_builtin(self) -> bool:
        return isinstance(self.url, BuiltInLanguageDefinitionURL)

    def __str__(self) -> str:
        return f"{self.alias}={self.url}"
