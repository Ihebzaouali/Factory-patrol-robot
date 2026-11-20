from typing import List

from rallp_config.common.types.accessory import Accessory
from rallp_config.mounts.types.mount import BaseMount


class Post(BaseMount):
    MOUNT_MODEL = 'post'
    HEIGHT = 0.075
    SPACING = 0.080
    SINGLE = 'single'
    DUAL = 'dual'
    QUAD = 'quad'
    MODELS = [SINGLE, DUAL, QUAD]

    def __init__(
            self,
            idx: int = None,
            name: str = None,
            model: str = SINGLE,
            height: float = HEIGHT,
            spacing: float = SPACING,
            parent: str = Accessory.PARENT,
            xyz: List[float] = Accessory.XYZ,
            rpy: List[float] = Accessory.RPY
            ) -> None:
        self.model = model
        self.height = height
        self.spacing = spacing
        super().__init__(idx, name, parent, xyz, rpy)

    def to_dict(self) -> dict:
        d = super().to_dict()
        d['model'] = self.get_model()
        d['height'] = self.height
        if self.get_model() != self.SINGLE:
            d['spacing'] = self.spacing
        return d

    def from_dict(self, d: dict) -> None:
        super().from_dict(d)
        if 'model' in d:
            self.set_model(d['model'])
        if 'height' in d:
            self.height = d['height']
        if 'spacing' in d:
            self.spacing = d['spacing']

    def get_model(self) -> str:
        return self.model

    def set_model(self, model: str) -> None:
        assert model in self.MODELS, f'Unexpected Post model "{model}". It must be one of "{self.MODELS}"'  # noqa:E501
        self.model = model

    @property
    def height(self) -> float:
        return self._height

    @height.setter
    def height(self, height: float) -> None:
        assert height > 0, (
            'Height must be positive "float"')
        self._height = height

    @property
    def spacing(self) -> float:
        return self._spacing

    @spacing.setter
    def spacing(self, spacing: float) -> None:
        assert spacing > 0, (
            'Spacing must be positive "float"')
        self._spacing = spacing
