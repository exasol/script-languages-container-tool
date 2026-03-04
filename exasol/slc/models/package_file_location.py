from pathlib import Path

_PACKAGE_FILE_NAME = "packages.yml"


class PackageFileLocation:
    def __init__(self, flavor_path: Path):
        self.flavor_path = flavor_path

    @property
    def public_package_file(self) -> Path:
        return self.flavor_path / _PACKAGE_FILE_NAME

    @property
    def internal_package_file(self) -> Path:
        return self.flavor_path / "flavor_base" / _PACKAGE_FILE_NAME
