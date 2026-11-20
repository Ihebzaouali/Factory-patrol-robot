from typing import List

from rallp_config.common.types.accessory import Accessory
from rallp_config.mounts.types.mount import BaseMount


class Disk(BaseMount):
    MOUNT_MODEL = 'disk'

    def __init__(
            self,
            idx: int = None,
            name: str = None,
            parent: str = Accessory.PARENT,
            xyz: List[float] = Accessory.XYZ,
            rpy: List[float] = Accessory.RPY
            ) -> None:
        super().__init__(idx, name, parent, xyz, rpy)
