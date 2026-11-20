import os

from ament_index_python.packages import get_package_share_directory

from rallp_config.rallp_config import RallpConfig
from rallp_config.common.utils.yaml import read_yaml

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    IncludeLaunchDescription,
    OpaqueFunction
)
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution
)

from launch_ros.actions import PushRosNamespace

from nav2_common.launch import RewrittenYaml


ARGUMENTS = [
    DeclareLaunchArgument('use_sim_time', default_value='false',
                          choices=['true', 'false'],
                          description='Use sim time'),
    DeclareLaunchArgument('setup_path',
                          default_value='/etc/rallp/',
                          description='Rallp setup path'),
    DeclareLaunchArgument('scan_topic',
                          default_value='',
                          description='Override the default 2D laserscan topic')
]


def launch_setup(context, *args, **kwargs):
    # Packages
    pkg_rallp_nav2_demos = get_package_share_directory('rallp_nav2_demos')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    # Launch Configurations
    use_sim_time = LaunchConfiguration('use_sim_time')
    setup_path = LaunchConfiguration('setup_path')
    map = LaunchConfiguration('map')  # noqa:A001
    scan_topic = LaunchConfiguration('scan_topic')

    # Read robot YAML
    config = read_yaml(os.path.join(setup_path.perform(context), 'robot.yaml'))
    # Parse robot YAML into config
    rallp_config = RallpConfig(config)

    namespace = rallp_config.system.namespace
    platform_model = rallp_config.platform.get_platform_model()

    eval_scan_topic = scan_topic.perform(context)
    if len(eval_scan_topic) == 0:
        eval_scan_topic = f'/{namespace}/sensors/lidar2d_0/scan'

    file_parameters = PathJoinSubstitution([
        pkg_rallp_nav2_demos,
        'config',
        platform_model,
        'localization.yaml'])

    rewritten_parameters = RewrittenYaml(
        source_file=file_parameters,
        param_rewrites={
            'scan_topic': eval_scan_topic,
        },
        convert_types=True
    )

    launch_localization = PathJoinSubstitution(
      [pkg_nav2_bringup, 'launch', 'localization_launch.py'])

    localization = GroupAction([
        PushRosNamespace(namespace),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(launch_localization),
            launch_arguments=[
                ('namespace', namespace),
                ('map', map),
                ('use_sim_time', use_sim_time),
                ('params_file', rewritten_parameters)
              ]
        ),
    ])

    return [localization]


def generate_launch_description():
    pkg_rallp_nav2_demos = get_package_share_directory('rallp_nav2_demos')

    map_arg = DeclareLaunchArgument(
        'map',
        default_value=PathJoinSubstitution([pkg_rallp_nav2_demos, 'maps', 'warehouse.yaml']),
        description='Full path to map yaml file to load')

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(map_arg)
    ld.add_action(OpaqueFunction(function=launch_setup))
    return ld
