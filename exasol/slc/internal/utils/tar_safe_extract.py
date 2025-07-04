import os
from tarfile import TarFile
from typing import List, Optional


def is_within_directory(directory: str, target: str) -> bool:
    abs_directory = os.path.abspath(directory)
    abs_target = os.path.abspath(target)

    prefix = os.path.commonprefix([abs_directory, abs_target])

    return prefix == abs_directory


def safe_extract(
    tar: TarFile,
    path: str = ".",
    members: Optional[list[str]] = None,
    *,
    numeric_owner: bool = False,
):
    """
    This function implements a patch for the CVE-2007-4559. The patch essentially checks
    to see if all tarfile members will be extracted safely and throws an exception otherwise.
    """
    for member in tar.getmembers():
        member_path = os.path.join(path, member.name)
        if not is_within_directory(path, member_path):
            raise Exception("Attempted Path Traversal in Tar File")

    tar.extractall(path=path, members=members, numeric_owner=numeric_owner)  # type: ignore
