import luigi


class CacheFileParameters:
    cache_file_path: str = luigi.Parameter()  # type: ignore
    checksum_file_path: str = luigi.Parameter()  # type: ignore
