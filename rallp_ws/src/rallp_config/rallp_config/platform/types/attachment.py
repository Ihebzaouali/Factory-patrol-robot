from typing import List

from rallp_config.common.types.accessory import Accessory
from rallp_config.common.types.platform import Platform


class BaseAttachment(Accessory):
    PLATFORM = Platform.GENERIC
    ATTACHMENT_MODEL = '%s.attachment' % PLATFORM
    ENABLED = True
    # Models
    DEFAULT = 'default'
    MODELS = [DEFAULT]

    def __init__(
            self,
            name: str = ATTACHMENT_MODEL,
            model: str = DEFAULT,
            enabled: bool = ENABLED,
            parent: str = ...,
            xyz: List[float] = ...,
            rpy: List[float] = ...
            ) -> None:
        super().__init__(name, parent, xyz, rpy)
        self.platform = self.ATTACHMENT_MODEL.split('.')[0]
        self.file = self.ATTACHMENT_MODEL.split('.')[-1]
        self.model = self.DEFAULT
        self.enabled = self.ENABLED
        self.set_model(model)
        self.set_enabled(enabled)

    def to_dict(self) -> dict:
        d = super().to_dict()
        d['type'] = self.ATTACHMENT_MODEL
        d['model'] = self.get_model()
        d['enabled'] = self.get_enabled()
        return d

    def from_dict(self, d: dict) -> None:
        super().from_dict(d)
        if 'model' in d:
            self.set_model(d['model'])
        if 'enabled' in d:
            self.set_enabled(d['enabled'])

    def set_enabled(self, enable: bool) -> None:
        self.enabled = bool(enable)

    def get_enabled(self) -> bool:
        return self.enabled

    def get_model(self) -> str:
        return self.model

    def set_model(self, model: str) -> None:
        assert model in self.MODELS, f'{self.ATTACHMENT_MODEL.title()} model "{model}" is not not of "{self.MODELS}"'  # noqa:E501
        self.model = model


class PlatformAttachment(BaseAttachment):
    PLATFORM = Platform.GENERIC
    TYPES = {}

    @classmethod
    def is_valid(cls, _type: str) -> bool:
        return _type in cls.TYPES

    def __new__(cls, _type: str) -> BaseAttachment:
        assert cls.is_valid(_type), f'{cls.PLATFORM} does not have attachment "{_type}". Must be one of "{cls.TYPES}"'  # noqa:E501
        return cls.TYPES[_type]
