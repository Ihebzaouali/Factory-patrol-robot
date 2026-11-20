from typing import List

from rallp_config.common.types.accessory import Accessory
from rallp_config.sensors.types.sensor import BaseSensor


class BaseCharger(BaseSensor):
    SENSOR_TYPE = 'charger'
    TOPIC = 'status'

    def __init__(
            self,
            idx: int = None,
            name: str = None,
            topic: str = TOPIC,
            urdf_enabled: bool = BaseSensor.URDF_ENABLED,
            launch_enabled: bool = BaseSensor.LAUNCH_ENABLED,
            ros_parameters: dict = BaseSensor.ROS_PARAMETERS,
            ros_parameters_template: dict = BaseSensor.ROS_PARAMETERS_TEMPLATE,
            parent: str = Accessory.PARENT,
            xyz: List[float] = Accessory.XYZ,
            rpy: List[float] = Accessory.RPY,
            ) -> None:
        super().__init__(
            idx,
            name,
            topic,
            urdf_enabled,
            launch_enabled,
            ros_parameters,
            ros_parameters_template,
            parent,
            xyz,
            rpy
        )


class Wiferion(BaseCharger):
    SENSOR_MODEL = 'wiferion'

    TOPIC = 'status'

    CANBUS_DEV = 'can0'

    class ROS_PARAMETER_KEYS:
        CANBUS_DEV = 'wiferion.canbus_dev'

    def __init__(
            self,
            idx: int = None,
            name: str = None,
            topic: str = TOPIC,
            canbus_dev: str = CANBUS_DEV,
            urdf_enabled: bool = BaseSensor.URDF_ENABLED,
            launch_enabled: bool = BaseSensor.LAUNCH_ENABLED,
            ros_parameters: dict = BaseSensor.ROS_PARAMETERS,
            ros_parameters_template: dict = BaseSensor.ROS_PARAMETERS_TEMPLATE,
            parent: str = Accessory.PARENT,
            xyz: List[float] = Accessory.XYZ,
            rpy: List[float] = Accessory.RPY,
            ) -> None:
        self.canbus_dev = canbus_dev
        ros_parameters_template = {
            self.ROS_PARAMETER_KEYS.CANBUS_DEV: Wiferion.canbus_dev,
        }
        super().__init__(
            idx,
            name,
            topic,
            urdf_enabled,
            launch_enabled,
            ros_parameters,
            ros_parameters_template,
            parent,
            xyz,
            rpy
        )

    @property
    def canbus_dev(self) -> str:
        return self._canbus_dev

    @canbus_dev.setter
    def canbus_dev(self, value: str) -> None:
        self._canbus_dev = value
