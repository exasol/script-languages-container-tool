from dataclasses import dataclass
from enum import Enum
from typing import List, Union
from urllib.parse import urlencode


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
    bucketfs_name: str
    bucket_name: str
    path_in_bucket: str
    container_name: str
    udf_client_path_within_container: str
    parameters: List[SLCParameter]
    language: SLCLanguage

    def __str__(self) -> str:
        query_params = {p.key: p.value for p in self.parameters}
        query_params["lang"] = [self.language.value.lower()]
        query_string = urlencode(query_params)
        path_in_bucket = self.path_in_bucket
        if path_in_bucket and not path_in_bucket.endswith("/"):
            path_in_bucket = f"{path_in_bucket}/"

        return (
            f"{self.protocol}:///{self.bucketfs_name}/{self.bucket_name}/{path_in_bucket}"
            f"{self.container_name}?{query_string}#buckets/{self.bucketfs_name}/{self.bucket_name}/"
            f"{path_in_bucket}{self.container_name}{self.udf_client_path_within_container}"
        )


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
        return type(self.url) is BuiltInLanguageDefinitionURL

    def __str__(self) -> str:
        return f"{self.alias}={self.url}"
