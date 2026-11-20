from typing import List

from rallp_config.common.types.accessory import Accessory
from rallp_config.platform.types.attachment import BaseAttachment


class Bumper(BaseAttachment):
    ATTACHMENT_MODEL = 'bumper'
    EXTENSION = 0.0
    DEFAULT = 'default'
    MODELS = [DEFAULT]

    def __init__(
            self,
            name: str = ATTACHMENT_MODEL,
            enabled: bool = BaseAttachment.ENABLED,
            model: str = DEFAULT,
            extension: float = EXTENSION,
            parent: str = Accessory.PARENT,
            xyz: List[float] = Accessory.XYZ,
            rpy: List[float] = Accessory.RPY
            ) -> None:
        super().__init__(
            name,
            enabled,
            model,
            parent,
            xyz,
            rpy
        )
        self.extension: float = Bumper.EXTENSION
        self.set_extension(extension)

    def to_dict(self) -> dict:
        d = super().to_dict()
        d['extension'] = self.extension
        return d

    def from_dict(self, d: dict) -> None:
        super().from_dict(d)
        if 'extension' in d:
            self.set_extension(d['extension'])

    def get_extension(self) -> float:
        return self.extension

    def set_extension(self, extension: float) -> None:
        try:
            extension = float(extension)
        except ValueError as e:
            raise AssertionError(e.args[0])
        assert isinstance(
            extension, float
        ), f'Bumper extension must be of type float, unexpected type {type(extension)}'
        assert extension >= 0, 'Bumper extension must be a positive value'
        self.extension = extension
