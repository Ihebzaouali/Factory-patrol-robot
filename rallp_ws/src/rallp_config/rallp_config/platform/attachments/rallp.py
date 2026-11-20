
from typing import List

from rallp_config.common.types.accessory import Accessory
from rallp_config.common.types.platform import Platform
from rallp_config.platform.types.attachment import BaseAttachment, PlatformAttachment
from rallp_config.platform.types.bumper import Bumper


class RallpTopPlate(BaseAttachment):
    PLATFORM = Platform.Rallp
    ATTACHMENT_MODEL = '%s.top_plate' % PLATFORM
    DEFAULT = 'default'
    PACS = 'pacs'
    MODELS = [DEFAULT, PACS]
    PARENT = 'default_mount'

    def __init__(
            self,
            name: str = ATTACHMENT_MODEL,
            model: str = DEFAULT,
            enabled: bool = BaseAttachment.ENABLED,
            parent: str = PARENT,
            xyz: List[float] = Accessory.XYZ,
            rpy: List[float] = Accessory.RPY
            ) -> None:
        super().__init__(name, model, enabled, parent, xyz, rpy)


class RallpBumper(Bumper):
    PLATFORM = Platform.Rallp
    ATTACHMENT_MODEL = '%s.bumper' % PLATFORM
    EXTENSION = 0.0
    DEFAULT = 'default'
    MODELS = [DEFAULT]
    PARENT = 'front_bumper_mount'

    def __init__(
            self,
            name: str = ATTACHMENT_MODEL,
            model: str = DEFAULT,
            enabled: bool = BaseAttachment.ENABLED,
            extension: float = EXTENSION,
            parent: str = PARENT,
            xyz: List[float] = Accessory.XYZ,
            rpy: List[float] = Accessory.RPY
            ) -> None:
        super().__init__(name, model, enabled, extension, parent, xyz, rpy)


class RallpWirelessCharger(BaseAttachment):
    PLATFORM = Platform.Rallp
    ATTACHMENT_MODEL = f'{PLATFORM}.wireless_charger'
    DEFAULT = 'default'
    MODELS = [DEFAULT]
    PARENT = 'base_link'

    def __init__(
            self,
            name: str = ATTACHMENT_MODEL,
            model: str = DEFAULT,
            enabled: bool = BaseAttachment.ENABLED,
            parent: str = PARENT,
            xyz: List[float] = Accessory.XYZ,
            rpy: List[float] = Accessory.RPY
            ) -> None:
        super().__init__(name, model, enabled, parent, xyz, rpy)


class RallpAmpEnclosure(BaseAttachment):
    PLATFORM = Platform.Rallp
    ATTACHMENT_MODEL = f'{PLATFORM}.amp_enclosure'
    AMP_ENCLOSURE = 'amp_enclosure'
    MODELS = [AMP_ENCLOSURE]
    DEFAULT = AMP_ENCLOSURE
    PARENT = 'base_link'

    def __init__(
            self,
            name: str = ATTACHMENT_MODEL,
            model: str = DEFAULT,
            enabled: bool = BaseAttachment.ENABLED,
            parent: str = PARENT,
            xyz: List[float] = Accessory.XYZ,
            rpy: List[float] = Accessory.RPY
            ) -> None:
        super().__init__(name, model, enabled, parent, xyz, rpy)


class RallpAmpSensorArch(BaseAttachment):
    PLATFORM = Platform.Rallp
    ATTACHMENT_MODEL = f'{PLATFORM}.amp_sensor_arch'
    AMP_SENSOR_ARCH = 'amp_sensor_arch'
    MODELS = [AMP_SENSOR_ARCH]
    DEFAULT = AMP_SENSOR_ARCH
    PARENT = 'default_mount'

    def __init__(
            self,
            name: str = ATTACHMENT_MODEL,
            model: str = DEFAULT,
            enabled: bool = BaseAttachment.ENABLED,
            parent: str = PARENT,
            xyz: List[float] = Accessory.XYZ,
            rpy: List[float] = Accessory.RPY
            ) -> None:
        super().__init__(name, model, enabled, parent, xyz, rpy)


class RallpSpotlight(BaseAttachment):
    PLATFORM = Platform.Rallp
    ATTACHMENT_MODEL = f'{PLATFORM}.spotlight'
    SPOTLIGHT = 'spotlight'
    MODELS = [SPOTLIGHT]
    DEFAULT = SPOTLIGHT
    PARENT = 'default_mount'

    def __init__(
            self,
            name: str = ATTACHMENT_MODEL,
            model: str = DEFAULT,
            enabled: bool = BaseAttachment.ENABLED,
            parent: str = PARENT,
            xyz: List[float] = Accessory.XYZ,
            rpy: List[float] = Accessory.RPY
            ) -> None:
        super().__init__(name, model, enabled, parent, xyz, rpy)


class RallpAttachment(PlatformAttachment):
    PLATFORM = Platform.Rallp
    # Top Plates
    TOP_PLATE = RallpTopPlate.ATTACHMENT_MODEL
    # Bumper
    BUMPER = RallpBumper.ATTACHMENT_MODEL
    # Observer/AMP attachments
    AMP_ENCLOSURE = RallpAmpEnclosure.ATTACHMENT_MODEL
    AMP_SENSOR_ARCH = RallpAmpSensorArch.ATTACHMENT_MODEL
    # Spotlight
    SPOTLIGHT = RallpSpotlight.ATTACHMENT_MODEL
    # Wireless charger
    WIRELESS_CHARGER = RallpWirelessCharger.ATTACHMENT_MODEL

    TYPES = {
        TOP_PLATE: RallpTopPlate,
        BUMPER: RallpBumper,
        AMP_ENCLOSURE: RallpAmpEnclosure,
        AMP_SENSOR_ARCH: RallpAmpSensorArch,
        SPOTLIGHT: RallpSpotlight,
        WIRELESS_CHARGER: RallpWirelessCharger,
    }
