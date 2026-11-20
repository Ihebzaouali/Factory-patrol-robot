from typing import List

from rallp_config.common.types.accessory import Accessory
from rallp_config.mounts.types.mount import BaseMount


class SICKStand(BaseMount):
    MOUNT_MODEL = 'sick'
    UPRIGHT = 'upright'
    INVERTED = 'inverted'
    MODELS = [UPRIGHT, INVERTED]

    def __init__(
            self,
            idx: int = None,
            name: str = None,
            model: str = INVERTED,
            parent: str = Accessory.PARENT,
            xyz: List[float] = Accessory.XYZ,
            rpy: List[float] = Accessory.RPY
            ) -> None:
        self.model = model
        super().__init__(idx, name, parent, xyz, rpy)

    def to_dict(self) -> dict:
        d = super().to_dict()
        d['model'] = self.get_model()
        return d

    def from_dict(self, d: dict) -> None:
        super().from_dict(d)
        if 'model' in d:
            self.set_model(d['model'])

    def get_model(self) -> str:
        return self.model

    def set_model(self, model: str) -> None:
        assert model in self.MODELS, f'Unexpected SICK stand model "{model}".  It must be one of "{self.MODELS}"'  # noqa:E501
        self.model = model
