def detect_container_file_extension(source_file: str) -> str:
    allowed_extensions = [".tar.gz", ".tar"]
    for suffix in allowed_extensions:
        if source_file.endswith(suffix):
            return suffix
    raise ValueError(
        f"File {source_file} does not end with one of {allowed_extensions}"
    )
