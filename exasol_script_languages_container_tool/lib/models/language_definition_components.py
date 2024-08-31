from dataclasses import dataclass
from enum import Enum
from pathlib import PurePosixPath
from typing import List, Optional, Union
from urllib.parse import ParseResult, urlencode, urlunparse


class SLCLanguage(Enum):
    Java = "java"
    Python3 = "python"
    R = "r"


@dataclass
class SLCParameter:
    key: str
    value: List[str]


@dataclass
class UdfClientBucketPath:
    bucketfs_name: str
    bucket_name: str
    executable: PurePosixPath

    def __str__(self) -> str:
        return f"buckets/{self.bucketfs_name}/{self.bucket_name}/" f"{self.executable}"


@dataclass
class UdfClientRelativePath:
    executable: PurePosixPath

    def __str__(self) -> str:
        return str(self.executable)


@dataclass
class ChrootPath:
    bucketfs_name: str
    bucket_name: str
    path_in_bucket: Optional[PurePosixPath] = None

    def __str__(self) -> str:
        return f"/{self.bucketfs_name}/{self.bucket_name}/{self.path_in_bucket or ''}"


@dataclass
class LanguageDefinitionURL:
    protocol: str
    parameters: List[SLCParameter]
    chroot_path: ChrootPath
    udf_client_path: Union[UdfClientBucketPath, UdfClientRelativePath]

    def __str__(self) -> str:
        query_params = {p.key: v for p in self.parameters for v in p.value}
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
    language: SLCLanguage

    def __str__(self) -> str:
        return f"builtin_{self.language.name.lower()}"


@dataclass
class LanguageDefinitionComponents:
    alias: str
    url: Union[LanguageDefinitionURL, BuiltInLanguageDefinitionURL]

    @property
    def is_builtin(self) -> bool:
        return isinstance(self.url, BuiltInLanguageDefinitionURL)

    def __str__(self) -> str:
        return f"{self.alias}={self.url}"
