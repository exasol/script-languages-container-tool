from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from typing import List, Union
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
    bucketfs_name: str
    bucket_name: str
    path_in_bucket: str
    container_name: str
    udf_client_path_within_container: str
    parameters: List[SLCParameter]
    language: SLCLanguage

    def __str__(self) -> str:
        Components = namedtuple(  # type: ignore
            typename="Components",
            field_names=[
                "scheme",
                "netloc",
                "url",
                "params",
                "query",
                "fragment",
            ],
        )

        query_params = {p.key: v for p in self.parameters for v in p.value}
        query_params["lang"] = self.language.value.lower()
        query_string = urlencode(query_params)
        path_in_bucket = self.path_in_bucket
        if path_in_bucket and not path_in_bucket.endswith("/"):
            path_in_bucket = f"{path_in_bucket}/"
        # this does not work:cannot instantiate ParseResult
        # url = urlunparse(
        #     ParseResult(
        #         fragment=f"buckets/{self.bucketfs_name}/{self.bucket_name}/{path_in_bucket}",
        #         hostname=None,
        #         netloc="",
        #         params="",
        #         password=None,
        #         path=f"/{self.bucketfs_name}/{self.bucket_name}/{self.path_in_bucket}/{self.container_name}",
        #         port=None,
        #         query=query_string,
        #         scheme=self.protocol,
        #         username=None,
        #     )
        # )
        url = urlunparse(
            Components(
                scheme=self.protocol,  # type: ignore
                netloc="",
                query=query_string,
                url=f"///{self.bucketfs_name}/{self.bucket_name}/{path_in_bucket}{self.container_name}",
                params="",
                fragment=f"buckets/{self.bucketfs_name}/{self.bucket_name}/{path_in_bucket}"
                f"{self.container_name}{self.udf_client_path_within_container}",
            )
        )
        return url  # type: ignore


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
