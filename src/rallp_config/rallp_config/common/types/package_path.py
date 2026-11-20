from rallp_config.common.types.file import File


class PackagePath:
    PACKAGE = 'package'
    PATH = 'path'

    def __init__(
            self,
            package: str = None,
            path: str = None,
            ) -> None:
        self.package = package
        self.path = File.clean(path, make_abs=False)

    def from_dict(self, config: dict) -> None:
        if self.PACKAGE in config:
            self.package = config[self.PACKAGE]
        if self.PATH in config:
            self.path = config[self.PATH]

    def to_dict(self) -> dict:
        return {
            self.PACKAGE: self.package,
            self.PATH: self.path,
        }

    @property
    def package(self) -> str:
        return self._package

    @package.setter
    def package(self, value: str) -> None:
        self._package = value

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str) -> None:
        self._path = value
