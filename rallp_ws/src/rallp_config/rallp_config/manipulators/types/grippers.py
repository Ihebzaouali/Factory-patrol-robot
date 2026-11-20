
from typing import List

from rallp_config.common.types.accessory import Accessory
from rallp_config.manipulators.types.manipulator import BaseManipulator


class BaseGripper(BaseManipulator):
    MANIPULATOR_MODEL = 'base'
    MANIPULATOR_TYPE = 'gripper'

    def __init__(
            self,
            arm: BaseManipulator,
            idx: int = None,
            name: str = None,
            ros_parameters: dict = BaseManipulator.ROS_PARAMETERS,
            ros_parameters_template: dict = BaseManipulator.ROS_PARAMETERS_TEMPLATE,
            parent: str = Accessory.PARENT,
            xyz: List[float] = Accessory.XYZ,
            rpy: List[float] = Accessory.RPY
            ) -> None:
        super().__init__(
            idx,
            name,
            ros_parameters,
            ros_parameters_template,
            parent,
            xyz,
            rpy,
        )
        self.arm = arm


class FrankaGripper(BaseGripper):
    MANIPULATOR_MODEL = 'franka_gripper'
    JOINT_COUNT = 1

    @property
    def arm_id(self) -> str:
        return self._arm_id

    @arm_id.setter
    def arm_id(self, value: str) -> None:
        self._arm_id = value


class Kinova2FLite(BaseGripper):
    MANIPULATOR_MODEL = 'kinova_2f_lite'
    JOINT_COUNT = 1

    USE_FAKE_HARDWARE = 'use_fake_hardware'
    USE_CONTROLLERS = 'use_controllers'
    FAKE_SENSOR_COMMANDS = 'fake_sensor_commands'
    SIM_IGNITION = 'sim_ignition'
    SIM_GAZEBO = 'sim_gazebo'
    SIM_ISAAC = 'sim_isaac'
    ISAAC_JOINT_COMMANDS = 'isaac_joint_commands'
    ISAAC_JOINT_STATES = 'isaac_joint_states'
    URDF_PARAMETERS = {
        USE_FAKE_HARDWARE: '',
        USE_CONTROLLERS: '',
        FAKE_SENSOR_COMMANDS: '',
        SIM_IGNITION: '',
        SIM_GAZEBO: '',
        SIM_ISAAC: '',
        ISAAC_JOINT_COMMANDS: '',
        ISAAC_JOINT_STATES: '',
    }


class Robotiq2F85(BaseGripper):
    MANIPULATOR_MODEL = 'robotiq_2f_85'
    JOINT_COUNT = 1

    USE_FAKE_HARDWARE = 'use_fake_hardware'
    USE_CONTROLLERS = 'use_controllers'
    FAKE_SENSOR_COMMANDS = 'fake_sensor_commands'
    SIM_IGNITION = 'sim_ignition'
    SIM_GAZEBO = 'sim_gazebo'
    SIM_ISAAC = 'sim_isaac'
    ISAAC_JOINT_COMMANDS = 'isaac_joint_commands'
    ISAAC_JOINT_STATES = 'isaac_joint_states'
    COM_PORT = 'com_port'
    URDF_PARAMETERS = {
        USE_FAKE_HARDWARE: '',
        USE_CONTROLLERS: '',
        FAKE_SENSOR_COMMANDS: '',
        SIM_IGNITION: '',
        SIM_GAZEBO: '',
        SIM_ISAAC: '',
        ISAAC_JOINT_COMMANDS: '',
        ISAAC_JOINT_STATES: '',
        COM_PORT: '',
    }


class Robotiq2F140(BaseGripper):
    MANIPULATOR_MODEL = 'robotiq_2f_140'
    JOINT_COUNT = 1
    USE_FAKE_HARDWARE = 'use_fake_hardware'
    USE_CONTROLLERS = 'use_controllers'
    FAKE_SENSOR_COMMANDS = 'fake_sensor_commands'
    SIM_IGNITION = 'sim_ignition'
    SIM_GAZEBO = 'sim_gazebo'
    SIM_ISAAC = 'sim_isaac'
    ISAAC_JOINT_COMMANDS = 'isaac_joint_commands'
    ISAAC_JOINT_STATES = 'isaac_joint_states'
    COM_PORT = 'com_port'
    URDF_PARAMETERS = {
        USE_FAKE_HARDWARE: '',
        USE_CONTROLLERS: '',
        FAKE_SENSOR_COMMANDS: '',
        SIM_IGNITION: '',
        SIM_GAZEBO: '',
        SIM_ISAAC: '',
        ISAAC_JOINT_COMMANDS: '',
        ISAAC_JOINT_STATES: '',
        COM_PORT: '',
    }


class Gripper():
    FRANKA_GRIPPER = FrankaGripper.MANIPULATOR_MODEL
    KINOVA_2F_LITE = Kinova2FLite.MANIPULATOR_MODEL
    ROBOTIQ_2F_140 = Robotiq2F140.MANIPULATOR_MODEL
    ROBOTIQ_2F_85 = Robotiq2F85.MANIPULATOR_MODEL

    MODEL = {
        FRANKA_GRIPPER: FrankaGripper,
        KINOVA_2F_LITE: Kinova2FLite,
        ROBOTIQ_2F_140: Robotiq2F140,
        ROBOTIQ_2F_85: Robotiq2F85,
    }

    @classmethod
    def assert_model(cls, model: str) -> None:
        assert model in cls.MODEL, f'Gripper model "{model}" must be one of "{cls.MODEL.keys()}"'

    def __new__(cls, arm: BaseManipulator, model: str) -> BaseGripper:
        cls.assert_model(model)
        return cls.MODEL[model](arm)
