from pathlib import Path

PACKAGE_FILE_NAME = "packages.yml"


class PackageFileLocation:
    def __init__(self, flavor_path: Path):
        self.flavor_path = flavor_path

    @property
    def public_package_file(self) -> Path:
        return self.flavor_path / PACKAGE_FILE_NAME

    @property
    def internal_package_file(self) -> Path:
        return self.flavor_path / "flavor_base" / PACKAGE_FILE_NAME
