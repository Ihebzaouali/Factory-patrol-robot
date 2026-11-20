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

from launch_ros.actions import PushRosNamespace, SetRemap

from nav2_common.launch import RewrittenYaml

# --- DYNAMIC PATH CALCULATION ---
home_dir = os.path.expanduser('~')
default_rallp_path = os.path.join(home_dir, 'rallp')
# --------------------------------

ARGUMENTS = [
    DeclareLaunchArgument('use_sim_time', default_value='false',
                          choices=['true', 'false'],
                          description='Use sim time'),
    DeclareLaunchArgument('setup_path',
                          # FIXED: No longer hardcoded to ubuntu24
                          default_value=default_rallp_path,
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
    scan_topic = LaunchConfiguration('scan_topic')

    # Read robot YAML - setup_path now resolves to /home/oussama/rallp
    config_file_path = os.path.join(setup_path.perform(context), 'robot.yaml')
    config = read_yaml(config_file_path)
    
    # Parse robot YAML into config
    rallp_config = RallpConfig(config)

    namespace = rallp_config.system.namespace
    platform_model = rallp_config.platform.get_platform_model()

    # see if we've overridden the scan_topic
    eval_scan_topic = scan_topic.perform(context)
    if len(eval_scan_topic) == 0:
        eval_scan_topic = f'/{namespace}/sensors/lidar2d_0/scan'

    file_parameters = PathJoinSubstitution([
        pkg_rallp_nav2_demos,
        'config',
        platform_model,
        'nav2.yaml'])

    rewritten_parameters = RewrittenYaml(
        source_file=file_parameters,
        param_rewrites={
            'topic': eval_scan_topic,
        },
        convert_types=True
    )

    launch_nav2 = PathJoinSubstitution(
      [pkg_nav2_bringup, 'launch', 'navigation_launch.py'])

    nav2 = GroupAction([
        PushRosNamespace(namespace),
        SetRemap('/' + namespace + '/odom',
                 '/' + namespace + '/platform/odom'),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(launch_nav2),
            launch_arguments=[
                ('use_sim_time', use_sim_time),
                ('params_file', rewritten_parameters),
                ('use_composition', 'False'),
                ('namespace', namespace)
              ]
        ),
    ])

    return [nav2]


def generate_launch_description():
    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(OpaqueFunction(function=launch_setup))
    return ld