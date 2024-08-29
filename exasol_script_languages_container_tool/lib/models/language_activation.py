from dataclasses import dataclass
from enum import Enum
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
class LanguageDefinitionURL:
    protocol: str
    chroot_bucketfs_name: str
    chroot_bucket_name: str
    udf_client_bucketfs_name: str
    udf_client_bucket_name: str
    udf_client_path_within_container: str
    parameters: List[SLCParameter]
    language: SLCLanguage
    chroot_path_in_bucket: str = ""
    udf_client_path_in_bucket: str = ""

    def __str__(self) -> str:
        query_params = {p.key: v for p in self.parameters for v in p.value}
        query_params["lang"] = self.language.value.lower()
        query_string = urlencode(query_params)
        url = urlunparse(
            ParseResult(
                scheme=self.protocol,
                netloc="",
                path=f"///{self.chroot_bucketfs_name}/{self.chroot_bucket_name}/{self.chroot_path_in_bucket}",
                params="",
                query=query_string,
                fragment=f"buckets/{self.udf_client_bucketfs_name}/{self.udf_client_bucket_name}/"
                f"{self.udf_client_path_in_bucket}{self.udf_client_path_within_container}",
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
