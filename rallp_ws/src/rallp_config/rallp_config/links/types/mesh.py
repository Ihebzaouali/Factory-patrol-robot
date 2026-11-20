from typing import List

from rallp_config.common.types.accessory import Accessory
from rallp_config.common.types.package_path import PackagePath
from rallp_config.links.types.link import BaseLink


class Mesh(BaseLink):
    LINK_TYPE = 'mesh'
    VISUAL = ''
    # COLLISION = 'empty.stl'

    def __init__(
            self,
            name: str,
            parent: str = Accessory.PARENT,
            visual: dict = VISUAL,
            # collision: float = COLLISION,
            xyz: List[float] = Accessory.XYZ,
            rpy: List[float] = Accessory.RPY,
            offset_xyz: List[float] = BaseLink.OFFSET_XYZ,
            offset_rpy: List[float] = BaseLink.OFFSET_RPY
            ) -> None:
        super().__init__(
            name,
            parent,
            xyz,
            rpy,
            offset_xyz,
            offset_rpy
        )

        self.visual: PackagePath = PackagePath(Mesh.VISUAL)
        self.set_visual(visual)

    def to_dict(self) -> dict:
        d = super().to_dict()
        d['visual'] = self.get_visual()
        return d

    def from_dict(self, d: dict) -> None:
        super().from_dict(d)
        if 'visual' in d:
            self.set_visual(d['visual'])

    def set_visual(self, visual: dict) -> None:
        if visual:
            self.visual.from_dict(visual)

    def get_visual(self) -> dict:
        return self.visual.to_dict()
